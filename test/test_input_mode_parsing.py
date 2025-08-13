import pytest, PHITS_tools
from pathlib import Path
from traceback import format_exc
import re, io
from conftest import path_to_base_phits_test_dir

phits_sample_dir = Path(path_to_base_phits_test_dir,'sample')
phits_recommendation_dir = Path(path_to_base_phits_test_dir,'recommendation')
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

potential_inputs_to_parse = [Path(f) for f in phits_sample_dir.rglob('*.inp')] + [Path(f) for f in phits_recommendation_dir.rglob('*.inp')]
inputs_to_parse = []
for f in potential_inputs_to_parse:
    if 'benchmark' in str(f): continue  # this directory has lots of problem folders with missing outputs
    if len([i for i in f.parent.glob('*.out')]) == 0: continue  # skip inputs in directories with no output files
    skip_this_input = False
    inputs_to_parse.append(f)

class TestState:
    def __init__(self, num_tests):
        self.log_buffer = io.StringIO()
        self.num_tests = num_tests
        self.i = 0
        self.num_passed = 0
        self.num_failed = 0
        self.num_warn = 0

@pytest.fixture(scope="session")
def test_state():
    state = TestState(len(inputs_to_parse))
    return state


def process_and_log_output_from_input_file(f, test_state):
    test_state.i += 1
    test_num_str = '{:3d}/{:3d}'.format(test_state.i, test_state.num_tests)
    try:
        x = PHITS_tools.parse_all_tally_output_in_dir(f, save_output_pickle=False, merge_tally_outputs=True,
                                                      save_pickle_of_merged_tally_outputs=True,
                                                      compress_pickle_with_lzma=True,
                                                      autoplot_all_tally_output_in_dir=test_autoplotting)
        log_str = test_num_str + '     pass  ' + str(f) + '\n'
        test_state.num_passed += 1
        status = 'pass'
    except Exception as e:
        if re.sub(r'^.*?phits', 'phits', str(f)) in known_issue_files:
            log_str = test_num_str + '  !  WARN  ' + str(f) + '\n'
            test_state.num_warn += 1
            status = 'WARN'
        else:
            log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
            status = 'FAIL'
        log_str += '\t\t' + repr(e) + '\n'
        log_str += '\t\t' + format_exc().replace('\n', '\n\t\t')
        log_str = log_str[:-2]
        test_state.num_failed += 1
    print(log_str)
    test_state.log_buffer.write(log_str)
    return status



@pytest.fixture(scope="session", autouse=True)
def final_log_summary(test_state):
    yield  # test session runs here
    # after all tests...
    log_str = '\n{:3d} of {:3d} tests passed\n'.format(test_state.num_passed, test_state.num_tests)
    log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(test_state.num_failed, test_state.num_tests)
    log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(test_state.num_warn, test_state.num_failed)
    print(log_str)
    test_state.log_buffer.write(log_str)
    with open(log_file_path, "w") as f:
        f.write(test_state.log_buffer.getvalue())

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize("file_path", inputs_to_parse)
def test_input_file_parsing_dir_mode(file_path, test_state):
    status = process_and_log_output_from_input_file(file_path, test_state)
    if status == "FAIL":
        pytest.fail(f"Processing failed for file: {file_path}", pytrace=False)
    assert status in ["pass", "WARN", "FAIL"]
