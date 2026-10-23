"""Source-document and repo contract tests, NOT application tests."""
from pathlib import Path
import csv
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_environment_names():
    names={line.partition('=')[0] for line in (ROOT/'.env.example').read_text().splitlines()
           if line and not line.startswith('#') and '=' in line}
    expected={'AWS_REGION','S3_BUCKET','S3_CURATED_PREFIX','S3_RUNS_PREFIX',
              'BEDROCK_MODEL_ID','C1V1C_OFFLINE_MODE','C1V1C_BASELINE_VERSION','C1V1C_MODEL_VERSION'}
    assert expected <= names
    assert 'C1V1C_S3_BUCKET' not in names


def test_official_and_master_documents_present():
    for p in ('docs/Original_Sustainable_Development_PS.docx','docs/C1V1C_Master_Plan.docx'):
        with zipfile.ZipFile(ROOT/p) as z:
            assert 'word/document.xml' in z.namelist()


def test_data_templates_are_intentionally_empty():
    for p in (ROOT/'data/templates').glob('*.csv'):
        with p.open(newline='', encoding='utf-8') as f:
            assert list(csv.DictReader(f))==[], p.name


def test_provenance_registry_does_not_claim_verified_measurements():
    with (ROOT/'data/source_registry.csv').open(newline='',encoding='utf-8') as f:
        records=list(csv.DictReader(f))
    assert len(records)>0
    assert all(r['verification_status']!='verified_observed_bengaluru' for r in records)
    fixture=json.loads((ROOT/'data/synthetic_test/fixture_manifest.json').read_text())
    assert fixture['status']=='synthetic_only_not_city_data'


def test_traceability_lists_all_mvp_components():
    m=(ROOT/'docs/REQUIREMENTS_TRACEABILITY.md').read_text()
    for id in ('PS-01','PS-02','PS-03','PS-04','PS-05'):
        assert re.search(r'\| '+id+r' \|',m)


def test_user_design_rulebook_included_and_mirrored():
    original=ROOT/'anti-slop-design.md'
    mirror=ROOT/'docs/ANTI_AI_SLOP.md'
    assert original.is_file() and mirror.is_file()
    assert original.read_bytes()==mirror.read_bytes()
    text=original.read_text(encoding='utf-8')
    for required in ('## 1. Phase 1', '## 2. Pick an archetype',
                     '## 3. Phase 2', '## 4. Banned defaults',
                     '## 6. Accessibility floor', '## 9. Slop check',
                     'overall ≥ 85', 'no category below 60'):
        assert required in text, f'Missing essential design rule: {required}'


def test_readme_contains_exact_user_design_instruction():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    assert 'I’ve attached **anti-slop-design.md**, the design rulebook for this project.' in readme
    assert 'run the §9 slop check before you show me anything.' in readme



def test_hyderabad_and_bucket_non_secret_configuration():
    entries = {}
    for line in (ROOT/'.env.example').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#') and '=' in line:
            k,v=line.split('=',1)
            entries[k]=v
    assert entries['AWS_REGION']=='ap-south-2'
    assert entries['S3_BUCKET']=='amzn-c1v1-bucket-515820372090-ap-south-2-an'
    assert entries['C1V1C_OFFLINE_MODE']=='true'
    assert entries['BEDROCK_MODEL_ID']==''
    assert not any(k in entries for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN'))


def test_git_ignores_local_secret_files():
    import subprocess
    for item in ('.env', '.env.production', 'nested/.env'):
        result=subprocess.run(['git','check-ignore','-q',item],cwd=ROOT)
        assert result.returncode==0, f'Not ignored: {item}'
    expected=subprocess.run(['git','check-ignore','-q','.env.example'],cwd=ROOT)
    assert expected.returncode!=0
    result=subprocess.run(['git','ls-files','--error-unmatch','.env'],cwd=ROOT,capture_output=True)
    assert result.returncode!=0, 'Local .env must never be tracked'


def test_aws_hyderabad_runbook_exists():
    s=(ROOT/'docs/AWS_HYDERABAD_SETUP.md').read_text(encoding='utf-8')
    assert 'ap-south-2' in s
    assert 'rotate' in s.lower()
    assert 'Bedrock' in s
