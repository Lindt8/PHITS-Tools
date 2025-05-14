import PHITS_tools
from pathlib import Path
from traceback import format_exc
import re

path_to_phits_base_folder = Path('C:\phits')

phits_sample_dir = Path(path_to_phits_base_folder,'sample')
phits_recommendation_dir = Path(path_to_phits_base_folder,'recommendation')
test_input_mode_parsing = True  # Determines if [INPUT_FILE mode] of parse_all_tally_output_in_dir() is tested for all input files
test_autoplotting = False  # Determines if autoplot_tally_results() is tested too for each tally output (notably slows testing)
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

log_file_str = ''
num_tests = len(files_to_parse)
i = 0
num_passed, num_failed, num_warn = 0, 0, 0
known_issue_files = [r'phits\sample\source\Cosmicray\GCR-ground\cross.out', r'phits\sample\source\Cosmicray\GCR-ground\GCR-ground.inp',
                     r'phits\sample\source\Cosmicray\GCR-LEO\cross.out', r'phits\sample\source\Cosmicray\GCR-LEO\GCR-LEO.inp',
                     r'phits\sample\source\Cosmicray\GCR-space\cross.out', r'phits\sample\source\Cosmicray\GCR-space\GCR-space.inp',
                     r'phits\sample\source\Cosmicray\SEP-space\cross.out', r'phits\sample\source\Cosmicray\SEP-space\SEP-space.inp',
                     r'phits\sample\source\Cosmicray\TP-LEO\cross.out', r'phits\sample\source\Cosmicray\TP-LEO\TP-LEO.inp',
                     r'phits\sample\misc\snowman\rotate3dshow.inp']
for f in files_to_parse:
    i += 1
    test_num_str = '{:3d}/{:3d}'.format(i,num_tests)
    try:
        if '_dmp.out' in str(f):
            x = PHITS_tools.parse_tally_dump_file(f, save_namedtuple_list=False, save_Pandas_dataframe=False)
        else:
            x = PHITS_tools.parse_tally_output_file(f, save_output_pickle=False, autoplot_tally_output=test_autoplotting)
            if test_autoplotting and Path(f.parent, f.stem + '.pdf').is_file(): plot_paths.append(Path(f.parent, f.stem + '.pdf'))
        log_str = test_num_str + '     pass  ' + str(f) + '\n'
        num_passed += 1
    except Exception as e:
        if re.sub(r'^.*?phits', 'phits', str(f)) in known_issue_files:
            log_str = test_num_str + '  !  WARN  ' + str(f) + '\n'
            num_warn += 1
        else:
            log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
        log_str += '\t\t' + repr(e) + '\n'
        log_str += '\t\t' + format_exc().replace('\n','\n\t\t')
        log_str = log_str[:-2]
        num_failed += 1
    print(log_str)
    log_file_str += log_str

log_str =  '\n{:3d} of {:3d} tests passed\n'.format(num_passed,num_tests)
log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(num_failed,num_tests)
log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(num_warn,num_failed)
print(log_str)
log_file_str += log_str


if test_input_mode_parsing:
    potential_inputs_to_parse = [Path(f) for f in phits_sample_dir.rglob('*.inp')] + [Path(f) for f in phits_recommendation_dir.rglob('*.inp')]
    inputs_to_parse = []
    for f in potential_inputs_to_parse:
        if 'benchmark' in str(f): continue  # this directory has lots of problem folders with missing outputs
        if len([i for i in f.parent.glob('*.out')]) == 0: continue  # skip inputs in directories with no output files
        skip_this_input = False
        inputs_to_parse.append(f)
    numi_passed, numi_failed, numi_warn = 0, 0, 0
    numi_tests = len(inputs_to_parse)
    log_str = '\n\n--------------------------------------------------------------------\n'
    log_str += 'INPUT FILE PARSING TESTS\n\n'
    log_file_str += log_str
    for f in inputs_to_parse:
        i += 1
        test_num_str = '{:3d}/{:3d}'.format(i, num_tests)
        try:
            x = PHITS_tools.parse_all_tally_output_in_dir(f, save_output_pickle=False, merge_tally_outputs=True,
                                                          save_pickle_of_merged_tally_outputs=True, compress_pickle_with_lzma=True,
                                                          autoplot_all_tally_output_in_dir=test_autoplotting)
            log_str = test_num_str + '     pass  ' + str(f) + '\n'
            numi_passed += 1
        except Exception as e:
            if re.sub(r'^.*?phits', 'phits', str(f)) in known_issue_files:
                log_str = test_num_str + '  !  WARN  ' + str(f) + '\n'
                numi_warn += 1
            else:
                log_str = test_num_str + '  x  FAIL  ' + str(f) + '\n'
            log_str += '\t\t' + repr(e) + '\n'
            log_str += '\t\t' + format_exc().replace('\n', '\n\t\t')
            log_str = log_str[:-2]
            numi_failed += 1
        print(log_str)
        log_file_str += log_str
    
    
    log_str =  '\n{:3d} of {:3d} tests passed\n'.format(numi_passed,numi_tests)
    log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(numi_failed,numi_tests)
    log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(numi_warn,numi_failed)
    print(log_str)
    log_file_str += log_str

    log_str = '\n\n--------------------------------------------------------------------\n'
    log_str += 'SUMMARY OVER ALL TESTING\n'
    log_str += '\n{:3d} of {:3d} tests passed\n'.format(numi_passed+num_passed, numi_tests+num_tests)
    log_str += '{:3d} of {:3d} tests failed (including "WARN")\n'.format(numi_failed+num_failed, numi_tests+num_tests)
    log_str += '{:3d} of {:3d} the failed tests are from old distributed files and should succeed if the corresponding PHITS input is reran (labeled with "WARN").\n'.format(numi_warn+num_warn, numi_failed+num_failed)
    print(log_str)
    log_file_str += log_str

# save log file
log_file_path = Path(Path.cwd(), 'test.log')
with open(log_file_path, "w") as f:
    f.write(log_file_str)

# compile generated PDFs into a single PDF
save_combined_pdf_of_plots = False
if test_autoplotting and save_combined_pdf_of_plots:
    from pypdf import PdfWriter
    merger = PdfWriter()
    plot_paths = sorted([str(i) for i in plot_paths], key=lambda x: (ord(x[-8]) % ord(x[-17]) + ord(x[-11]) % ord(x[-25]) - min(ord(x[-24]), ord(x[-31])) % ord(x[-12]) + ord(x[-18]) % ord(x[-9]), ord(x[-30]), len(x)), reverse=False)  # very arbitrary trial-and-error-found resorting of the files that put the "more interesting" plots first
    for pdf in plot_paths: 
        merger.append(pdf)
    merger.write("test_tally_plots.pdf")
    merger.close()