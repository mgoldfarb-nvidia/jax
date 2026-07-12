# Copyright 2026 The JAX Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pathlib
import tempfile
import unittest

from jaxlib.tools import build_utils


class CopyFileTest(unittest.TestCase):

  class _DirectoryRunfiles:

    def __init__(self, root: pathlib.Path):
      self._root = root

    def Rlocation(self, path: str) -> str:
      return str(self._root / path)

  def test_optional_source_is_copied_when_present(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      root = pathlib.Path(temp_dir)
      source = root / "runtime-source.so"
      source.write_bytes(b"runtime")
      destination = root / "wheel"

      copied = build_utils.copy_file(
          "runtime-source.so",
          destination,
          dst_filename="libcute_dsl_runtime.so",
          wheel_sources_map={"runtime-source.so": str(source)},
          required=False,
      )

      self.assertTrue(copied)
      self.assertEqual(
          (destination / "libcute_dsl_runtime.so").read_bytes(), b"runtime"
      )

  def test_optional_source_is_skipped_when_absent(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      destination = pathlib.Path(temp_dir) / "wheel"

      copied = build_utils.copy_file(
          "missing.so",
          destination,
          wheel_sources_map={"other.so": "unused"},
          required=False,
      )

      self.assertFalse(copied)
      self.assertEqual(list(destination.iterdir()), [])

  def test_optional_directory_runfile_is_skipped_when_absent(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      root = pathlib.Path(temp_dir)
      destination = root / "wheel"

      copied = build_utils.copy_file(
          "missing.so",
          destination,
          runfiles=self._DirectoryRunfiles(root),
          required=False,
      )

      self.assertFalse(copied)
      self.assertEqual(list(destination.iterdir()), [])

  def test_optional_sources_are_not_partially_copied(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      root = pathlib.Path(temp_dir)
      source = root / "present.so"
      source.write_bytes(b"runtime")
      destination = root / "wheel"

      copied = build_utils.copy_file(
          ["present.so", "missing.so"],
          destination,
          wheel_sources_map={"present.so": str(source)},
          required=False,
      )

      self.assertFalse(copied)
      self.assertEqual(list(destination.iterdir()), [])

  def test_required_source_remains_an_error(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      with self.assertRaisesRegex(ValueError, "missing.so"):
        build_utils.copy_file(
            "missing.so",
            pathlib.Path(temp_dir),
            wheel_sources_map={"other.so": "unused"},
        )


if __name__ == "__main__":
  unittest.main()
