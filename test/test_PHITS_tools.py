import PHITS_tools
from pathlib import Path


path_to_phits_base_folder = Path('C:\phits')

phits_sample_dir = Path(path_to_phits_base_folder,'sample')
phits_recommendation_dir = Path(path_to_phits_base_folder,'recommendation')

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


log_file_str = ''
num_tests = len(files_to_parse)
i = 0
num_passed = 0
num_failed = 0
num_warn = 0
known_issue_files = []
for f in files_to_parse:
    i += 1
    test_num_str = '{:3d}/{:3d}'.format(i,num_tests)
    try:
        x = PHITS_tools.parse_tally_output_file(f,save_output_pickle=False)
        log_str = test_num_str + '     pass  ' + str(f) + '\n'
        num_passed += 1
    except Exception as e:
        log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
        log_str += '\t\t' + str(e) + '\n'
        num_failed += 1
    print(log_str)
    log_file_str += log_str

log_str =  '\n{:3d} of {:3d} tests passed\n'.format(num_passed,num_tests)
log_str += '{:3d} of {:3d} tests failed\n'.format(num_failed,num_tests)
log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the PHITS input is reran.\n'.format(num_warn,num_failed)
print(log_str)
log_file_str += log_str

# save log file
log_file_path = Path(Path.cwd(), 'test.log')
with open(log_file_path, "w") as f:
    f.write(log_file_str)
