#!/usr/bin/env python3
"""Tests for update_cask.py. Run: python3 -m unittest discover -s tools

The signature tests use the real minisign binary (from the dev shell) with a
throwaway key, so they check the exact command line the workflow runs.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import update_cask

SHA = "b32b74236de72cc6a6d857109d976a93605377c236e6405a6c7137b679175dc2"


def manifest(**overrides):
    data = {
        "schema": 1,
        "channel": "beta",
        "version": "2.7.0-alpha",
        "build": 54610,
        "platforms": {
            "macos-arm64": {
                "url": "https://mixxx.xetk.co.uk/updates/mixxx-b54610-macos-arm64.dmg",
                "sha256": SHA,
                "size": 1,
            },
        },
    }
    data.update(overrides)
    return json.dumps(data)


def accept(*_args, **_kwargs):
    return subprocess.CompletedProcess([], 0, "", "")


class CaskFieldsTest(unittest.TestCase):
    def test_reads_the_macos_build(self):
        self.assertEqual(update_cask.cask_fields(manifest()),
                         {"version": "2.7.0-alpha", "build": 54610, "sha256": SHA})

    def test_rejects_bad_manifests(self):
        mac = json.loads(manifest())["platforms"]["macos-arm64"]
        bad = [
            "not json",
            "[]",
            manifest(version="2.7.0\"; system"),
            manifest(version=None),
            manifest(build="54610"),
            manifest(build=True),
            manifest(build=0),
            manifest(platforms={}),
            manifest(platforms=None),
            manifest(platforms={"macos-arm64": "x"}),
            manifest(platforms={"macos-arm64": {**mac, "sha256": "ABC"}}),
            manifest(platforms={"macos-arm64": {**mac, "sha256": None}}),
            manifest(platforms={"macos-arm64": {**mac, "url": "https://evil.example/m.dmg"}}),
            manifest(build=54611),  # url names a different build
        ]
        for text in bad:
            with self.subTest(text=text), self.assertRaises(update_cask.FeedError):
                update_cask.cask_fields(text)


class RenderTest(unittest.TestCase):
    def test_cask_has_version_checksum_and_derived_url(self):
        cask = update_cask.render({"version": "2.7.0-alpha", "build": 54610, "sha256": SHA})
        self.assertIn('cask "mixxx-fork" do\n', cask)
        self.assertIn('  version "2.7.0-alpha,54610"\n', cask)
        self.assertIn(f'  sha256 "{SHA}"\n', cask)
        self.assertIn(
            '  url "https://mixxx.xetk.co.uk/updates/mixxx-b#{version.csv.second}-macos-arm64.dmg"\n',
            cask)
        self.assertIn('"#{json["version"]},#{json["build"]}"', cask)
        self.assertIn('  app "Mixxx.app"\n', cask)

    @unittest.skipUnless(shutil.which("ruby"), "ruby not on PATH")
    def test_cask_is_valid_ruby(self):
        cask = update_cask.render({"version": "2.7.0-alpha", "build": 54610, "sha256": SHA})
        result = subprocess.run(["ruby", "-c"], input=cask, capture_output=True, text=True,
                                check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifest = self.tmp / "latest.json"
        self.manifest.write_text(manifest())
        self.sig = self.tmp / "latest.json.minisig"
        self.sig.write_text("sig")
        self.out = self.tmp / "Casks" / "mixxx-fork.rb"

    def test_writes_then_reports_unchanged(self):
        self.assertTrue(update_cask.update(self.manifest, self.sig, self.out, run=accept))
        self.assertIn("54610", self.out.read_text())
        self.assertFalse(update_cask.update(self.manifest, self.sig, self.out, run=accept))

    def test_rewrites_when_the_build_changes(self):
        update_cask.update(self.manifest, self.sig, self.out, run=accept)
        newer = json.loads(manifest(build=54700))
        newer["platforms"]["macos-arm64"]["url"] = (
            "https://mixxx.xetk.co.uk/updates/mixxx-b54700-macos-arm64.dmg")
        self.manifest.write_text(json.dumps(newer))
        self.assertTrue(update_cask.update(self.manifest, self.sig, self.out, run=accept))
        self.assertIn('version "2.7.0-alpha,54700"', self.out.read_text())

    def test_bad_signature_writes_nothing(self):
        def reject(*_args, **_kwargs):
            return subprocess.CompletedProcess([], 1, "", "Signature verification failed")
        with self.assertRaisesRegex(update_cask.FeedError, "verification failed"):
            update_cask.update(self.manifest, self.sig, self.out, run=reject)
        self.assertFalse(self.out.exists())

    def test_main_prints_result_and_exit_code(self):
        args = ["--manifest", str(self.manifest), "--signature", str(self.sig), "--out", str(self.out)]
        with mock.patch("builtins.print") as printed:
            self.assertEqual(update_cask.main(args, run=accept), 0)
            printed.assert_called_with("changed")
            self.assertEqual(update_cask.main(args, run=accept), 0)
            printed.assert_called_with("unchanged")
        self.manifest.write_text("[]")
        with mock.patch("builtins.print"):
            self.assertEqual(update_cask.main(args, run=accept), 1)


@unittest.skipUnless(shutil.which("minisign"), "minisign not on PATH")
class MinisignTest(unittest.TestCase):
    """verify() against real minisign signatures."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pub, sec = self.tmp / "key.pub", self.tmp / "key.sec"
        subprocess.run(["minisign", "-G", "-W", "-p", pub, "-s", sec], check=True,
                       capture_output=True)
        self.public_key = pub.read_text().splitlines()[1]
        self.manifest = self.tmp / "latest.json"
        self.manifest.write_text(manifest())
        self.sig = self.tmp / "latest.json.minisig"
        subprocess.run(["minisign", "-S", "-s", sec, "-m", self.manifest, "-x", self.sig],
                       check=True, capture_output=True)

    def test_accepts_a_good_signature(self):
        update_cask.verify(self.manifest, self.sig, public_key=self.public_key)

    def test_rejects_a_tampered_manifest(self):
        self.manifest.write_text(manifest(build=1))
        with self.assertRaises(update_cask.FeedError):
            update_cask.verify(self.manifest, self.sig, public_key=self.public_key)

    def test_rejects_another_key(self):
        with self.assertRaises(update_cask.FeedError):
            update_cask.verify(self.manifest, self.sig)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
