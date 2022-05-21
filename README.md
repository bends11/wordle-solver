## Building the comparisons.json file
Execute the following commands to build the comparisons.json file. This is required to use the `wordle_common.fast_compare()` function
```bash
echo [] > comparisons.json
python build_comparison_dict.py
sed -i "y/'/\"/" output.json
mv output.json comparisons.json
```
