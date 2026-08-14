"""Unit tests for agentive_kit.door — the packaged setup door (KIT-0104).

The resolve/validate layer runs in-process with no filesystem side
effects (the bootstrap F1 internal-decomposition contract, ported).
The matrix cells asserted here are THE single implementation of
shape × profile legality in the packaged world — after the bootstrap
shim lands, no shell copy remains.

E2E coverage (subprocess runs of ``agentive new/adopt``) lives in
test_door_e2e.py; the data-store sync guard in
tests/test_door_data_sync.py.
"""

from __future__ import annotations

import os

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import door  # noqa: E402


def run_door_main(mode, argv):
    with pytest.raises(SystemExit) as exc_info:
        door.main(mode, argv)
    return exc_info.value.code


class TestMatrix:
    """F2: the matrix, door-owned data — the packaged single owner."""

    @pytest.mark.parametrize(
        "shape,profile",
        [("single", "python"), ("single", "none"), ("planning", "none")],
    )
    def test_legal_cells(self, shape, profile):
        assert door.validate_pair(shape, profile) is True

    def test_illegal_cell_names_legal_pairs(self, capsys):
        assert door.validate_pair("planning", "python") is False
        err = capsys.readouterr().err
        assert "illegal shape/profile combination" in err
        assert "single+python (default)" in err

    def test_unknown_shape_rejected(self, capsys):
        assert door.validate_values("pyramid", "") is False
        assert "unknown shape" in capsys.readouterr().err

    def test_unknown_profile_rejected(self, capsys):
        assert door.validate_values("single", "elixir") is False
        assert "unknown profile" in capsys.readouterr().err

    def test_unresolved_profile_allowed(self):
        assert door.validate_values("single", "") is True


class TestDefaults:
    def test_kit_default_shape_is_single(self):
        assert door.kit_default("shape") == "single"

    @pytest.mark.parametrize(
        "shape,expected", [("single", "python"), ("planning", "none"), ("", "python")]
    )
    def test_kit_default_profile_follows_shape(self, shape, expected):
        assert door.kit_default("profile", shape) == expected

    def test_no_default_for_other_keys(self):
        assert door.kit_default("bots") is None


class TestResolveSetting:
    def test_cli_wins_over_everything(self):
        assert (
            door.resolve_setting(
                "shape", "planning", {"shape": "single"}, record={"shape": "single"}
            )
            == "planning"
        )

    def test_preset_beats_kit_default(self):
        assert door.resolve_setting("shape", "", {"shape": "planning"}) == "planning"

    def test_record_short_circuits_preset(self):
        # a question the record already answered is not open — the
        # preset is not consulted; the chain falls to the kit default
        assert (
            door.resolve_setting(
                "profile",
                "",
                {"profile": "none"},
                "single",
                {"profile": "none"},
            )
            == "python"
        )

    def test_empty_preset_answer_falls_through(self):
        assert door.resolve_setting("shape", "", {"shape": ""}) == "single"

    def test_unanswered_unknown_key_returns_none(self):
        assert door.resolve_setting("bots", "", {}) is None


class TestNormalizeBots:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("coderabbit bugbot", "coderabbit bugbot"),
            ("bugbot coderabbit", "coderabbit bugbot"),
            ("BugBot, CodeRabbit", "coderabbit bugbot"),
            ("coderabbit", "coderabbit"),
            ("bugbot", "bugbot"),
            ("none", "none"),
            ("NONE", "none"),
        ],
    )
    def test_canonical_forms(self, raw, expected):
        assert door.normalize_bots(raw) == expected

    def test_unknown_bot_rejected(self):
        with pytest.raises(ValueError, match="unknown bot 'dependabot'"):
            door.normalize_bots("dependabot")

    def test_none_combined_rejected(self):
        with pytest.raises(ValueError, match="cannot be combined"):
            door.normalize_bots("none coderabbit")

    def test_empty_input_is_unanswered_not_error(self):
        assert door.normalize_bots("") is None
        assert door.normalize_bots(" , ") is None


class TestPreset:
    def _load(self, tmp_path, content, no_preset=False):
        cfg = tmp_path / "agentive-config"
        cfg.mkdir(exist_ok=True)
        (cfg / "preset").write_text(content, encoding="utf-8")
        return door.load_preset(cfg, no_preset)

    def test_flat_keys_parsed(self, tmp_path):
        data, path = self._load(tmp_path, "shape: planning\nprofile: none\n")
        assert data == {"shape": "planning", "profile": "none"}
        assert path is not None

    def test_no_preset_flag_disables_the_layer(self, tmp_path):
        data, path = self._load(tmp_path, "shape: planning\n", no_preset=True)
        assert data == {}
        assert path is None

    def test_missing_home_answers_nothing(self, tmp_path):
        data, path = door.load_preset(tmp_path / "no-such-home", False)
        assert data == {}
        assert path is None

    def test_unknown_key_warns_and_skips_never_errors(self, tmp_path, capsys):
        data, _ = self._load(tmp_path, "flavor: spicy\nshape: single\n")
        assert data == {"shape": "single"}
        assert "unknown preset key 'flavor'" in capsys.readouterr().err

    def test_malformed_line_fails_loud_naming_the_line(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            self._load(tmp_path, "shape: single\njust some words\n")
        assert exc_info.value.code == 2
        err = capsys.readouterr().err
        assert "malformed preset line 2" in err

    def test_duplicate_key_fails_loud(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            self._load(tmp_path, "shape: single\nshape: planning\n")
        assert exc_info.value.code == 2
        assert "duplicate preset key 'shape'" in capsys.readouterr().err

    def test_comments_blanks_and_crlf_tolerated(self, tmp_path):
        data, _ = self._load(tmp_path, "# a comment\r\n\r\nshape: planning\r\n")
        assert data == {"shape": "planning"}

    def test_empty_value_falls_through(self, tmp_path):
        data, _ = self._load(tmp_path, "shape:\n")
        assert door.preset_get(data, "shape") is None

    def test_non_utf8_preset_exits_2_never_tracebacks(self, tmp_path, capsys):
        # fast-gate evaluator, this PR: a preset the door cannot decode
        # is a usage problem to fix, never an unhandled UnicodeDecodeError
        cfg = tmp_path / "agentive-config"
        cfg.mkdir()
        (cfg / "preset").write_bytes(b"shape: \xff\xfe single\n")
        with pytest.raises(SystemExit) as exc_info:
            door.load_preset(cfg, False)
        assert exc_info.value.code == 2
        assert "could not read preset" in capsys.readouterr().err


class TestConfigHome:
    """Packaged-world anchor: <target-parent>/agentive-config, with
    AGENTIVE_KIT_CONFIG_DIR as the ONE override (operator decision,
    2026-08-13)."""

    def test_target_parent_sibling(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AGENTIVE_KIT_CONFIG_DIR", raising=False)
        target = tmp_path / "projects" / "my-app"
        assert door.config_home(target) == tmp_path / "projects" / "agentive-config"

    def test_env_override_wins(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AGENTIVE_KIT_CONFIG_DIR", str(tmp_path / "cfg"))
        assert door.config_home(tmp_path / "elsewhere" / "app") == tmp_path / "cfg"

    def test_tilde_user_form_expanded(self):
        # deep evaluator: ~user/dir must expand via expanduser (the
        # bash door's ${1/#~/$HOME} mangled that form); an unresolvable
        # user stays literal, and a mid-string ~ is never touched
        import getpass

        me = getpass.getuser()
        expanded = door._expand_tilde(f"~{me}/cfg")
        assert not expanded.startswith("~")
        assert door._expand_tilde("/a/~b") == "/a/~b"

    def test_env_override_expands_tilde(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AGENTIVE_KIT_CONFIG_DIR", "~/kit-cfg")
        home = door.config_home(tmp_path / "app")
        assert str(home) == os.path.expanduser("~") + "/kit-cfg"


class TestParseArgs:
    def test_equals_and_split_forms(self):
        opts = door.parse_args(
            "new", ["--shape=planning", "--profile", "none", "dir-a"]
        )
        assert opts.shape_cli == "planning"
        assert opts.profile_cli == "none"
        assert opts.target_raw == "dir-a"

    @pytest.mark.parametrize("argv", [["dir", "--shape"], ["dir", "--shape="]])
    def test_value_flag_with_no_value_is_usage_error(self, argv, capsys):
        # deep evaluators (o3 + claude-code, convergent): the bash door
        # let a trailing '--shape' silently resolve to the kit default;
        # the packaged door surfaces the mistake (masking class)
        with pytest.raises(SystemExit) as exc_info:
            door.parse_args("new", argv)
        assert exc_info.value.code == 2
        assert "requires a value" in capsys.readouterr().err

    def test_value_flag_must_not_swallow_following_flag(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            door.parse_args("new", ["--shape", "--profile", "none"])
        assert exc_info.value.code == 2
        assert "requires a value" in capsys.readouterr().err

    def test_unknown_argument_is_usage(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            door.parse_args("new", ["--frobnicate"])
        assert exc_info.value.code == 2
        assert "unknown argument" in capsys.readouterr().err

    def test_multiple_targets_rejected(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            door.parse_args("adopt", ["dir-a", "dir-b"])
        assert exc_info.value.code == 2
        assert "multiple target directories" in capsys.readouterr().err

    def test_help_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            door.parse_args("new", ["--help"])
        assert exc_info.value.code == 0
        assert "shape" in capsys.readouterr().out

    def test_switch_flags(self):
        opts = door.parse_args(
            "adopt", ["dir", "--no-kit", "--without-venv", "--no-preset"]
        )
        assert opts.no_kit is True
        assert opts.with_venv == "no"
        assert opts.no_preset is True


class TestUsageText:
    """F6: /new-project derives its interview from this help at
    runtime — every door flag must appear in it, and no factory-clone
    language may (the packaged help is born clean, F5)."""

    @pytest.mark.parametrize("mode", ["new", "adopt"])
    def test_every_flag_documented(self, mode):
        text = door.usage_text(mode)
        for flag in (
            "--shape",
            "--profile",
            "--name",
            "--prefix",
            "--target-path",
            "--target-github",
            "--no-kit",
            "--bots",
            "--with-evaluators",
            "--without-evaluators",
            "--with-venv",
            "--without-venv",
            "--no-preset",
            "--design-materials",
        ):
            assert flag in text, f"{flag} missing from agentive {mode} --help"

    @pytest.mark.parametrize("mode", ["new", "adopt"])
    def test_no_factory_clone_language(self, mode):
        text = door.usage_text(mode).lower()
        assert "kit-side only" not in text
        assert "from an agentive-starter-kit clone" not in text
        assert "runs from anywhere" in text

    @pytest.mark.parametrize("mode", ["new", "adopt"])
    def test_matrix_and_preset_documented(self, mode):
        text = door.usage_text(mode)
        assert "planning" in text
        assert "agentive-config" in text
        assert "AGENTIVE_KIT_CONFIG_DIR" in text


class TestLoadRecord:
    def _write(self, tmp_path, body):
        (tmp_path / "CLAUDE.md").write_text(
            "# X\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            f"{body}\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_fields_parsed(self, tmp_path):
        target = self._write(
            tmp_path,
            "shape: planning\nprofile: none\n"
            "target_path: ../prod\ntarget_github: acme/prod\nbots: none",
        )
        rec = door.load_record(target)
        assert rec == {
            "shape": "planning",
            "profile": "none",
            "target_path": "../prod",
            "target_github": "acme/prod",
            "bots": "none",
        }

    def test_whitespace_tolerant(self, tmp_path):
        target = self._write(tmp_path, "  shape:   single  \n\tprofile:\tnone")
        rec = door.load_record(target)
        assert rec["shape"] == "single"
        assert rec["profile"] == "none"

    def test_crlf_record_values_are_trimmed(self, tmp_path):
        # BugBot, this PR: a CRLF CLAUDE.md leaves \r before the
        # MULTILINE $ — values like 'single\r' would false-conflict
        # with identical flags and break every == comparison downstream
        (tmp_path / "CLAUDE.md").write_bytes(
            b"# X\r\n\r\n<!-- BEGIN KIT-LOCAL: kit-install -->\r\n"
            b"shape: single\r\nprofile: none\r\n"
            b"<!-- END KIT-LOCAL: kit-install -->\r\n"
        )
        rec = door.load_record(tmp_path)
        assert rec["shape"] == "single"
        assert rec["profile"] == "none"

    def test_absent_region_loads_nothing(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("# plain\n", encoding="utf-8")
        assert door.load_record(tmp_path) == {}

    def test_missing_file_loads_nothing(self, tmp_path):
        assert door.load_record(tmp_path) == {}

    def test_non_utf8_file_loads_nothing_never_tracebacks(self, tmp_path):
        # BugBot round 2: UnicodeDecodeError is not an OSError — the
        # documented best-effort contract (load nothing, the engine
        # fails loud later) must hold for undecodable files too
        (tmp_path / "CLAUDE.md").write_bytes(b"\xff\xfe garbage \xff\n")
        assert door.load_record(tmp_path) == {}


def _resolved_opts(mode="new", **overrides):
    opts = door.DoorOptions(mode)
    opts.shape = overrides.pop("shape", "single")
    opts.profile = overrides.pop("profile", "python")
    opts.effective_profile = overrides.pop("effective_profile", opts.profile)
    for key, value in overrides.items():
        setattr(opts, key, value)
    return opts


class TestValidateCombo:
    def test_default_new_is_legal(self):
        assert door.validate_combo(_resolved_opts()) is True

    @pytest.mark.parametrize("mode", ["new", "adopt"])
    def test_no_kit_single_is_legal_from_both_verbs(self, mode):
        """KIT-0104 F4: rung 0 is reachable from new AND adopt."""
        assert door.validate_combo(_resolved_opts(mode=mode, no_kit=True)) is True

    @pytest.mark.parametrize(
        "kwargs,fragment",
        [
            (
                {
                    "mode": "adopt",
                    "shape": "planning",
                    "profile": "none",
                    "no_kit": True,
                },
                "--no-kit contradicts --shape planning",
            ),
            (
                {"mode": "new", "no_kit": True, "name": "x"},
                "--no-kit targets get no scaffold",
            ),
            (
                {"mode": "new", "no_kit": True, "prefix": "XX"},
                "--no-kit targets get no scaffold",
            ),
            (
                {"mode": "new", "design_materials": "yes"},
                "--design-materials applies to --adopt",
            ),
            (
                {"mode": "adopt", "name": "x"},
                "--name/--prefix apply to --new only",
            ),
            (
                {"mode": "new", "target_path": "../x"},
                "apply to the planning shape only",
            ),
            (
                {
                    "mode": "adopt",
                    "profile": "none",
                    "with_venv": "yes",
                },
                "--with-venv requires profile python",
            ),
            (
                {
                    "mode": "adopt",
                    "profile": "none",
                    "design_materials": "yes",
                },
                "--design-materials requires profile python",
            ),
            (
                {
                    "mode": "adopt",
                    "design_materials": "yes",
                    "no_kit": True,
                },
                "--no-kit contradicts --design-materials",
            ),
            (
                {
                    "mode": "new",
                    "shape": "planning",
                    "profile": "none",
                    "name": "x",
                },
                "--name/--prefix apply to '--new --shape single'",
            ),
        ],
    )
    def test_illegal_combos(self, capsys, kwargs, fragment):
        assert door.validate_combo(_resolved_opts(**kwargs)) is False
        assert fragment in capsys.readouterr().err


class TestFillEnvIdentity:
    def _opts(self, tmp_path, shape="single", prefix=""):
        opts = door.DoorOptions("new")
        opts.target = tmp_path
        opts.shape = shape
        opts.prefix = prefix
        return opts

    def test_duplicate_identity_lines_deduplicated(self, tmp_path):
        (tmp_path / ".env").write_text(
            "PROJECT_NAME=old\nOTHER=x\nPROJECT_NAME=older\n"
            "TASK_PREFIX=A\nTASK_PREFIX=B\n",
            encoding="utf-8",
        )
        door.fill_env_identity(self._opts(tmp_path, prefix="KIT"))
        lines = (tmp_path / ".env").read_text(encoding="utf-8").splitlines()
        assert lines.count(f"PROJECT_NAME={tmp_path.name}") == 1
        assert sum(1 for ln in lines if ln.startswith("PROJECT_NAME")) == 1
        assert sum(1 for ln in lines if ln.startswith("TASK_PREFIX")) == 1
        assert "OTHER=x" in lines

    def test_export_prefixed_and_indented_lines_matched(self, tmp_path):
        (tmp_path / ".env").write_text(
            "  export PROJECT_NAME=old\n\texport TASK_PREFIX=OLD\n",
            encoding="utf-8",
        )
        door.fill_env_identity(self._opts(tmp_path, prefix="NEW"))
        text = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "old" not in text
        assert "TASK_PREFIX=NEW" in text

    def test_missing_lines_appended(self, tmp_path):
        (tmp_path / ".env").write_text("OTHER=1\n", encoding="utf-8")
        door.fill_env_identity(self._opts(tmp_path, prefix="KIT"))
        lines = (tmp_path / ".env").read_text(encoding="utf-8").splitlines()
        assert f"PROJECT_NAME={tmp_path.name}" in lines
        assert "TASK_PREFIX=KIT" in lines

    def test_planning_writes_empty_prefix_never_placeholder(self, tmp_path):
        (tmp_path / ".env").write_text("TASK_PREFIX=TASK\n", encoding="utf-8")
        door.fill_env_identity(self._opts(tmp_path, shape="planning"))
        lines = (tmp_path / ".env").read_text(encoding="utf-8").splitlines()
        assert "TASK_PREFIX=" in lines

    def test_recorded_prefix_wins_over_flag(self, tmp_path):
        state = tmp_path / ".kit" / "context"
        state.mkdir(parents=True)
        (state / "current-state.json").write_text(
            '{"project": {"task_prefix": "REC"}}', encoding="utf-8"
        )
        (tmp_path / ".env").write_text("TASK_PREFIX=x\n", encoding="utf-8")
        door.fill_env_identity(self._opts(tmp_path, prefix="FLAG"))
        assert "TASK_PREFIX=REC" in (tmp_path / ".env").read_text(encoding="utf-8")

    def test_null_recorded_prefix_never_writes_none(self, tmp_path):
        state = tmp_path / ".kit" / "context"
        state.mkdir(parents=True)
        (state / "current-state.json").write_text(
            '{"project": {"task_prefix": null}}', encoding="utf-8"
        )
        (tmp_path / ".env").write_text("TASK_PREFIX=x\n", encoding="utf-8")
        door.fill_env_identity(self._opts(tmp_path))
        text = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "None" not in text

    def test_no_env_file_is_a_quiet_noop(self, tmp_path):
        door.fill_env_identity(self._opts(tmp_path))
        assert not (tmp_path / ".env").exists()

    def test_special_char_name_written_quoted(self, tmp_path):
        spaced = tmp_path / "my app"
        spaced.mkdir()
        (spaced / ".env").write_text("PROJECT_NAME=x\n", encoding="utf-8")
        door.fill_env_identity(self._opts(spaced))
        assert 'PROJECT_NAME="my app"' in (spaced / ".env").read_text(encoding="utf-8")

    def test_mode_is_0600_after_rewrite(self, tmp_path):
        (tmp_path / ".env").write_text("A=1\n", encoding="utf-8")
        door.fill_env_identity(self._opts(tmp_path))
        assert (tmp_path / ".env").stat().st_mode & 0o777 == 0o600


class TestCopyEnvGuard:
    """The one writer of target/.env refuses unless .env is gitignored
    — the critical KIT-0084 guardrail (fast-gate test-gap finding)."""

    def _repo(self, tmp_path, gitignore_body):
        import subprocess

        target = tmp_path / "repo"
        target.mkdir()
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(target)],
            check=True,
            timeout=30,
        )
        if gitignore_body is not None:
            (target / ".gitignore").write_text(gitignore_body, encoding="utf-8")
        source = tmp_path / "source.env"
        source.write_text("KEY=value\n", encoding="utf-8")
        return target, source

    def test_refuses_when_env_not_gitignored(self, tmp_path, capsys):
        target, source = self._repo(tmp_path, "other-stuff\n")
        with pytest.raises(SystemExit) as exc_info:
            door.copy_env_into_target(target, source)
        assert exc_info.value.code == 1
        assert ".env is not gitignored" in capsys.readouterr().err
        assert not (target / ".env").exists(), "refusal must not write"

    def test_writes_0600_when_gitignored(self, tmp_path):
        target, source = self._repo(tmp_path, ".env\n")
        door.copy_env_into_target(target, source)
        env_path = target / ".env"
        assert env_path.read_text(encoding="utf-8") == "KEY=value\n"
        assert env_path.stat().st_mode & 0o777 == 0o600

    def test_refuses_to_write_through_env_symlink(self, tmp_path, capsys):
        # deep evaluator: a pre-planted .env symlink must never be
        # followed — the gitignore check sees the symlink path, not
        # its referent (O_NOFOLLOW)
        target, source = self._repo(tmp_path, ".env\n")
        victim = tmp_path / "victim-file"
        victim.write_text("precious\n", encoding="utf-8")
        (target / ".env").symlink_to(victim)
        with pytest.raises(SystemExit) as exc_info:
            door.copy_env_into_target(target, source)
        assert exc_info.value.code == 1
        assert "symlink" in capsys.readouterr().err
        assert victim.read_text(encoding="utf-8") == "precious\n"


class TestSyncPairs:
    """The staging maps must stay internally consistent."""

    def test_every_pair_resolves_to_a_packaged_file(self):
        pairs = door.sync_pairs()
        assert pairs, "sync manifest must not be empty"
        for repo_rel, pkg_path in pairs:
            assert pkg_path.is_file(), f"packaged copy missing: {pkg_path}"
            assert not repo_rel.startswith("/")

    def test_stage_destinations_never_overlap(self):
        # claude-code evaluator: overlapping staged paths would let a
        # later _STAGE_MAP entry silently overwrite an earlier one —
        # pin uniqueness across BOTH maps
        destinations = list(door._STAGE_MAP.values()) + list(door._ENGINE_MAP.values())
        assert len(destinations) == len(set(destinations))

    def test_engines_dir_ships_exactly_the_invocable_set(self):
        # engine-materials.sh is deliberately NOT packaged: it rsyncs a
        # kit working tree and execs an interactive agent — unreachable
        # from the packaged door; its successor is project-intake
        # (KIT-ADR-0031).
        # is_file(): pip byte-compiles installed kit_markers.py, so a
        # non-editable install grows __pycache__/ here (CodeRabbit)
        names = sorted(p.name for p in door._ENGINES_DIR.iterdir() if p.is_file())
        assert names == [
            "engine-consumer.sh",
            "engine-scaffold.sh",
            "kit_markers.py",
        ]
