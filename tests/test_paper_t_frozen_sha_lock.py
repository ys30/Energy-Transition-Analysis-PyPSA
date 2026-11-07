import hashlib
import pytest
from energy_transition.paper_t_frozen_sha_lock import audit,REQUIRED

def setup(tmp_path):
    root=tmp_path/"evidence"
    entries=[]
    for path in sorted(REQUIRED):
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(("verified-"+path).encode())
        entries.append(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+path)
    lock=tmp_path/"lock.txt";lock.write_text("# Source frozen\n"+"\n".join(entries)+"\n")
    return lock,root

def test_exact_original_bundle_hashes(tmp_path):
    lock,root=setup(tmp_path)
    assert audit(lock,root)["source_evidence_files_checked"]==16
    assert not audit(lock,root)["permanent_DOI_registered"]

def test_changed_original_file_rejected(tmp_path):
    lock,root=setup(tmp_path)
    p=root/"tables/T_S1_nonwrapping_33_state_year_lags.csv"
    p.write_text("mutated evidence")
    with pytest.raises(ValueError,match="CHANGED"):audit(lock,root)

def test_lock_scope_incomplete_rejected(tmp_path):
    lock,root=setup(tmp_path)
    lock.write_text("\n".join(lock.read_text().splitlines()[:-1])+"\n")
    with pytest.raises(ValueError,match="exactly 16"):audit(lock,root)

def test_invalid_hash_lock_rejected(tmp_path):
    lock,root=setup(tmp_path)
    lock.write_text(lock.read_text()+"this isn't sha256\n")
    with pytest.raises(ValueError,match="Invalid"):audit(lock,root)
