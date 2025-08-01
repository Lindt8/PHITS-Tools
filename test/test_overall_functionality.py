import pytest, PHITS_tools
from pathlib import Path
from traceback import format_exc
import re

path_to_phits_base_folder = Path(r'C:\phits')

phits_sample_dir = Path(path_to_phits_base_folder,'sample')
phits_recommendation_dir = Path(path_to_phits_base_folder,'recommendation')
test_autoplotting = True  # Determines if autoplot_tally_results() is tested too for each tally output (notably slows testing)
plot_paths = []

sample_files = phits_sample_dir.rglob('*.out')
recommendation_files = phits_recommendation_dir.rglob('*.out')
files_to_parse = []
skip_strs = ['phits.out','batch.out','WWG','3dshow']
for f in sample_files:
    keep_file = True
    for s in skip_strs:
        if s in str(f):
            keep_file = False
    if keep_file:
        files_to_parse.append(Path(f))
for f in recommendation_files:
    keep_file = True
    for s in skip_strs:
        if s in str(f):
            keep_file = False
    if keep_file:
        files_to_parse.append(Path(f))

log_file_path = Path(__file__).parent / 'test_overall_functionality.log'
log_file_str = ''
log_str = ''
num_tests = len(files_to_parse)
i = 0
num_passed, num_failed, num_warn = 0, 0, 0
known_issue_files = [r'phits\sample\source\Cosmicray\GCR-ground\cross.out', r'phits\sample\source\Cosmicray\GCR-ground\GCR-ground.inp',
                     r'phits\sample\source\Cosmicray\GCR-LEO\cross.out', r'phits\sample\source\Cosmicray\GCR-LEO\GCR-LEO.inp',
                     r'phits\sample\source\Cosmicray\GCR-space\cross.out', r'phits\sample\source\Cosmicray\GCR-space\GCR-space.inp',
                     r'phits\sample\source\Cosmicray\SEP-space\cross.out', r'phits\sample\source\Cosmicray\SEP-space\SEP-space.inp',
                     r'phits\sample\source\Cosmicray\TP-LEO\cross.out', r'phits\sample\source\Cosmicray\TP-LEO\TP-LEO.inp',
                     r'phits\sample\misc\snowman\rotate3dshow.inp']

# save log file, deleting any old contents
with open(log_file_path, "w") as f:
    f.write(log_file_str)

def process_and_log_output_file(f):
    global log_str, log_file_str, i, num_passed, num_failed, num_warn
    i += 1
    test_num_str = '{:3d}/{:3d}'.format(i, num_tests)
    try:
        if '_dmp.out' in str(f):
            x = PHITS_tools.parse_tally_dump_file(f, save_namedtuple_list=False, save_Pandas_dataframe=False)
        else:
            x = PHITS_tools.parse_tally_output_file(f, save_output_pickle=False,
                                                    autoplot_tally_output=test_autoplotting)
            if test_autoplotting and Path(f.parent, f.stem + '.pdf').is_file(): plot_paths.append(
                Path(f.parent, f.stem + '.pdf'))
        log_str = test_num_str + '     pass  ' + str(f) + '\n'
        num_passed += 1
        status = 'pass'
    except Exception as e:
        if re.sub(r'^.*?phits', 'phits', str(f)) in known_issue_files:
            log_str = test_num_str + '  !  WARN  ' + str(f) + '\n'
            num_warn += 1
            status = 'WARN'
        else:
            log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
            status = 'FAIL'
        log_str += '\t\t' + repr(e) + '\n'
        log_str += '\t\t' + format_exc().replace('\n', '\n\t\t')
        log_str = log_str[:-2]
        num_failed += 1
    print(log_str)
    log_file_str += log_str
    # update the log file
    with open(log_file_path, "a") as f:
        f.write(log_str)
    return status


@pytest.fixture(scope="session", autouse=True)
def final_log_summary():
    global num_passed, num_tests, num_failed, num_warn
    yield  # test session runs here
    # after all tests...
    log_str = '\n{:3d} of {:3d} tests passed\n'.format(num_passed, num_tests)
    log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(num_failed, num_tests)
    log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(num_warn, num_failed)
    print(log_str)
    with open(log_file_path, "a") as f:
        f.write(log_str)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize("file_path", files_to_parse)
def test_individual_output_parsing(file_path):
    status = process_and_log_output_file(file_path)
    if status == "FAIL":
        pytest.fail(f"Processing failed for file: {file_path}", pytrace=False)
    assert status in ["pass", "WARN", "FAIL"]


# compile generated PDFs into a single PDF
# Only works if running the script normally, not via pytest
save_combined_pdf_of_plots = False
if test_autoplotting and save_combined_pdf_of_plots:
    test_individual_output_parsing()
    from pypdf import PdfWriter
    merger = PdfWriter()
    plot_paths = sorted([str(i) for i in plot_paths], key=lambda x: (ord(x[-8]) % ord(x[-17]) + ord(x[-11]) % ord(x[-25]) - min(ord(x[-24]), ord(x[-31])) % ord(x[-12]) + ord(x[-18]) % ord(x[-9]), ord(x[-30]), len(x)), reverse=False)  # very arbitrary trial-and-error-found resorting of the files that put the "more interesting" plots first
    for pdf in plot_paths: 
        merger.append(pdf)
    merger.write("test_tally_plots.pdf")
    merger.close()