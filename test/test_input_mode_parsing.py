import pytest, PHITS_tools
from pathlib import Path
from traceback import format_exc
import re

path_to_phits_base_folder = Path(r'C:\phits')

phits_sample_dir = Path(path_to_phits_base_folder,'sample')
phits_recommendation_dir = Path(path_to_phits_base_folder,'recommendation')
test_autoplotting = True  # Determines if autoplot_tally_results() is tested too for each tally output (notably slows testing)
known_issue_files = [r'phits\sample\source\Cosmicray\GCR-ground\cross.out', r'phits\sample\source\Cosmicray\GCR-ground\GCR-ground.inp',
                     r'phits\sample\source\Cosmicray\GCR-LEO\cross.out', r'phits\sample\source\Cosmicray\GCR-LEO\GCR-LEO.inp',
                     r'phits\sample\source\Cosmicray\GCR-space\cross.out', r'phits\sample\source\Cosmicray\GCR-space\GCR-space.inp',
                     r'phits\sample\source\Cosmicray\SEP-space\cross.out', r'phits\sample\source\Cosmicray\SEP-space\SEP-space.inp',
                     r'phits\sample\source\Cosmicray\TP-LEO\cross.out', r'phits\sample\source\Cosmicray\TP-LEO\TP-LEO.inp',
                     r'phits\sample\misc\snowman\rotate3dshow.inp']

sample_files = phits_sample_dir.rglob('*.out')
recommendation_files = phits_recommendation_dir.rglob('*.out')

log_file_path = Path(__file__).parent / 'test_input_mode_parsing.log'
log_file_str = ''
log_str = ''
i = 0
numi_passed, numi_failed, numi_warn = 0, 0, 0

potential_inputs_to_parse = [Path(f) for f in phits_sample_dir.rglob('*.inp')] + [Path(f) for f in phits_recommendation_dir.rglob('*.inp')]
inputs_to_parse = []
for f in potential_inputs_to_parse:
    if 'benchmark' in str(f): continue  # this directory has lots of problem folders with missing outputs
    if len([i for i in f.parent.glob('*.out')]) == 0: continue  # skip inputs in directories with no output files
    skip_this_input = False
    inputs_to_parse.append(f)
numi_tests = len(inputs_to_parse)
#log_str = '\n\n--------------------------------------------------------------------\n'
#log_str += 'INPUT FILE PARSING TESTS\n\n'
#log_file_str += log_str

# save log file, deleting any old contents
with open(log_file_path, "w") as f:
    f.write(log_file_str)


def process_and_log_output_from_input_file(f):
    global log_str, log_file_str, i, numi_passed, numi_failed, numi_warn
    i += 1
    test_num_str = '{:3d}/{:3d}'.format(i, numi_tests)
    try:
        x = PHITS_tools.parse_all_tally_output_in_dir(f, save_output_pickle=False, merge_tally_outputs=True,
                                                      save_pickle_of_merged_tally_outputs=True,
                                                      compress_pickle_with_lzma=True,
                                                      autoplot_all_tally_output_in_dir=test_autoplotting)
        log_str = test_num_str + '     pass  ' + str(f) + '\n'
        numi_passed += 1
        status = 'pass'
    except Exception as e:
        if re.sub(r'^.*?phits', 'phits', str(f)) in known_issue_files:
            log_str = test_num_str + '  !  WARN  ' + str(f) + '\n'
            numi_warn += 1
            status = 'WARN'
        else:
            log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
            status = 'FAIL'
        log_str += '\t\t' + repr(e) + '\n'
        log_str += '\t\t' + format_exc().replace('\n', '\n\t\t')
        log_str = log_str[:-2]
        numi_failed += 1
    print(log_str)
    log_file_str += log_str
    # save log file
    with open(log_file_path, "a") as f:
        f.write(log_str)
    return status



@pytest.fixture(scope="session", autouse=True)
def final_log_summary():
    global numi_passed, numi_tests, numi_failed, numi_warn
    yield  # test session runs here
    # after all tests...
    log_str = '\n{:3d} of {:3d} tests passed\n'.format(numi_passed, numi_tests)
    log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(numi_failed, numi_tests)
    log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(numi_warn, numi_failed)
    print(log_str)
    with open(log_file_path, "a") as f:
        f.write(log_str)

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize("file_path", inputs_to_parse)
def test_input_file_parsing_dir_mode(file_path):
    status = process_and_log_output_from_input_file(file_path)
    if status == "FAIL":
        pytest.fail(f"Processing failed for file: {file_path}", pytrace=False)
    assert status in ["pass", "WARN", "FAIL"]
