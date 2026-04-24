"""
Namespace package import test — run by ci/test_namespace_pkg.sh after both
edgegrid-python and the temporary akamai-dummy fragment are installed.
Requires REPO_DIR env var pointing to the edgegrid-python repo root.
"""
import akamai
import akamai.dummy
import akamai.edgegrid
import os

from akamai.dummy import SENTINEL
from akamai.edgegrid import EdgeGridAuth, EdgeRc

assert SENTINEL == "akamai.dummy is here", f"Unexpected value: {SENTINEL!r}"

# Exercise real EdgeRc code — parse the sample_edgerc shipped with the package.
sample_edgerc = os.path.join(os.environ["REPO_DIR"], "akamai", "edgegrid", "test", "sample_edgerc")
rc = EdgeRc(sample_edgerc)
assert rc.get("default", "host") == "xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx.luna.akamaiapis.net/", "EdgeRc.get failed"

# Both fragments must live under the *same* namespace package object.
# Each entry in akamai.__path__ is the `akamai/` dir from one fragment.
# Derive expected dirs by going up one level from each sub-package's __file__.
real_paths = [os.path.realpath(p) for p in akamai.__path__ if os.path.isdir(p)]

edgegrid_frag = os.path.realpath(os.path.join(os.path.dirname(akamai.edgegrid.__file__), ".."))
dummy_frag    = os.path.realpath(os.path.join(os.path.dirname(akamai.dummy.__file__),   ".."))

assert edgegrid_frag in real_paths, f"edgegrid fragment {edgegrid_frag!r} not in {real_paths}"
assert dummy_frag    in real_paths, f"dummy fragment {dummy_frag!r} not in {real_paths}"

print(f"OK — akamai.edgegrid is reachable from {edgegrid_frag}")
print(f"OK — akamai.dummy    is reachable from {dummy_frag}")
