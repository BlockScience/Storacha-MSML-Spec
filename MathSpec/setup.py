from math_spec_mapping import (load_from_json, write_spec_tree, write_parameter_table, write_all_markdown_reports, remove_dummy_repo_components)

from copy import deepcopy
from src import math_spec_json

ms = load_from_json(deepcopy(math_spec_json))


markdown_dir = "./Markdown"
scaffold_dir = "./Scaffold"
write_all_markdown_reports(ms, markdown_dir, clear_folders=True)
write_spec_tree(ms, path=markdown_dir, linking=True)
write_parameter_table(ms, path=markdown_dir, linking=True)
write_all_markdown_reports(ms, scaffold_dir, clear_folders=False)