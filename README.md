# textract_json_to_df

Create Pandas dataframes of tables from a json file produced by AWS textract. Especially, the code merges columns correctly which is an issue with the current methods provided by AWS or other open-source packages at the time of writing (June 2023).

For instance, if you look at the current state-of-the-art library to use with AWS Textract (https://aws-samples.github.io/amazon-textract-textractor/index.html), you will find the example of the "Consolidated Statement of Cash Flows" (https://aws-samples.github.io/amazon-textract-textractor/notebooks/table_data_to_various_formats.html#Calling-Textract) and you will see that the column headers "Three Month Ended June 30", "Six Month Ended June 30" and "Twelve Month Ended June 30" are split in the Excel even if they should be consolidated for each column. (That is, "Three Month Ended June 30" should appear in Columns B and C in the Excel, "Six Month Ended June 30" should appear in Columns D and E in the Excel, etc.)

Another example is given in the notebook [`textract-merged-cols-failure-and-solution.ipynb`](https://github.com/fascani/textract_json_to_df/blob/main/textract-merged-cols-failure-and-solution.ipynb) together with how to implement a solution with  [`from_textract_json_to_df.py`](https://github.com/fascani/textract_json_to_df/blob/main/from_textract_json_to_df.py).

The trick used to merge columns successfully is to use the `LINE` objects instead of the `CELL` objects to fill up the dataframe and, in a second step, and to merge the content of columns that need to be merged using the `MERGED_CELL` objects.
