import pandas as pd

def get_table_blocks(blocks):
  table_blocks = []
  for block in blocks:
      if block['BlockType'] == 'TABLE':
          table_blocks.append(block)
  return table_blocks
  
def get_cell_blocks(blocks):
  cell_blocks = []
  for block in blocks:
      if block['BlockType'] == 'CELL':
          cell_blocks.append(block)
  return cell_blocks
  
 def get_line_blocks(blocks):
  line_blocks = []
  for block in blocks:
      if block['BlockType'] == 'LINE':
          line_blocks.append(block)
  return line_blocks
  
def get_merged_cell_blocks(blocks):
  merged_cell_blocks = []
  for block in blocks:
      if block['BlockType'] == 'MERGED_CELL':
          merged_cell_blocks.append(block)
  return merged_cell_blocks
  
def construct_table_child_ids(table_blocks):
  '''
  Return dictionaries of table that have childs. The first dictionary has table ids as keys
  and the content is the list of child ids. The second dictionary has child id as keys and return
  the table id they are part of. If the cell exists in more than one table, keep only one table id.
  '''
  table_child_ids = {}
  child_table_ids = {}
  for table_block in table_blocks:
      if 'Relationships' in table_block.keys():
          # Find childs
          ii = 0
          max_ii = len(table_block['Relationships'])
          while (table_block['Relationships'][ii]['Type'] != 'CHILD')&(ii<max_ii):
              ii += 1
          if ii < max_ii: # Only do this if a CHILD relationship was found
              child_ids = table_block['Relationships'][ii]['Ids']
              table_child_ids[table_block['Id']] = child_ids
              for child_id in child_ids:
                  if child_id not in child_table_ids.keys(): # Don't add the child id if a cell was already found
                      child_table_ids[child_id] = table_block['Id']

  return table_child_ids, child_table_ids
  
def construct_table_merged_cell_ids(table_blocks):
  '''
  Return dictionaries of table that have merged cells. The first dictionary has table ids as keys
  and the ids of the merged cells. The second dictionary has the merged cell ids as keys and return
  the table id they are part of.
  '''
  table_merged_cell_ids = {}
  merged_cell_table_ids = {}
  for table_block in table_blocks:
      if 'Relationships' in table_block.keys():
          # Find merged cells
          ii = 0
          max_ii = len(table_block['Relationships'])
          while (table_block['Relationships'][ii]['Type'] != 'MERGED_CELL')&(ii<max_ii):
              ii += 1
          if ii < max_ii: # Only do this if a CHILD relationship was found
              merged_cell_ids = table_block['Relationships'][ii]['Ids']
              table_merged_cell_ids[table_block['Id']] = merged_cell_ids
              for merged_cell_id in merged_cell_ids:
                  if merged_cell_id not in merged_cell_table_ids.keys(): # Don't add the child id if a cell was already found
                      merged_cell_table_ids[merged_cell_id] = table_block['Id']

  return table_merged_cell_ids, merged_cell_table_ids
  
def construct_cell_child_ids(cell_blocks):
  '''
  Return dictionaries of cell that have childs. The first dictionary has cell ids as keys
  and the content is the list of child ids. The second dictionary has child id as keys and return
  the cell id they are part of. If the word exists in more than one cell, keep only one cell id.
  '''
  cell_child_ids = {}
  child_cell_ids = {}
  for cell_block in cell_blocks:
      if 'Relationships' in cell_block.keys():
          ii = 0
          max_ii = len(cell_block['Relationships'])
          while (cell_block['Relationships'][ii]['Type'] != 'CHILD')&(ii<max_ii):
              ii += 1
          if ii < max_ii: # Only do this if a CHILD relationship was found
              child_ids = cell_block['Relationships'][ii]['Ids']
              cell_child_ids[cell_block['Id']] = child_ids
              for child_id in child_ids:
                  if child_id not in child_cell_ids.keys(): # Don't add the child id if a cell was already found
                      child_cell_ids[child_id] = cell_block['Id']
                      
  return cell_child_ids, child_cell_ids
  
def construct_merged_cell_child_ids(merged_cell_blocks):
  '''
  Return dictionaries of table that have childs. The first dictionary has table ids as keys
  and the content is the list of child ids. The second dictionary has child id as keys and return
  the table id they are part of. If the cell exists in more than one table, keep only one table id.
  '''
  merged_cell_child_ids = {}
  child_merged_cell_ids = {}
  for merged_cell_block in merged_cell_blocks:
      if 'Relationships' in merged_cell_block.keys():
          # Find childs
          ii = 0
          max_ii = len(merged_cell_block['Relationships'])
          while (merged_cell_block['Relationships'][ii]['Type'] != 'CHILD')&(ii<max_ii):
              ii += 1
          if ii < max_ii: # Only do this if a CHILD relationship was found
              child_ids = merged_cell_block['Relationships'][ii]['Ids']
              merged_cell_child_ids[merged_cell_block['Id']] = child_ids
              for child_id in child_ids:
                  if child_id not in child_merged_cell_ids.keys(): # Don't add the child id if a cell was already found
                      child_merged_cell_ids[child_id] = merged_cell_block['Id']

  return merged_cell_child_ids, child_merged_cell_ids
  
def build_df(textract_json):
  '''
  From json output from textract, build Pandas dataframes filled up with the LINE object.
  To do so, we find the parent table and parent cell the first word of a LINE object may be part of.
  '''

  # Get blocks
  blocks = textract_json['Blocks']
  table_blocks = get_table_blocks(blocks)
  cell_blocks = get_cell_blocks(blocks)
  line_blocks = get_line_blocks(blocks)
  merged_cell_blocks = get_merged_cell_blocks(blocks)

  # Get the dictionaries linking cells to their childs
  cell_child_ids, child_cell_ids = construct_cell_child_ids(cell_blocks)

  # Get the dictionaries linking tables to their childs
  table_child_ids, child_table_ids = construct_table_child_ids(table_blocks)

  # Get the dictionaries linking tables to their merged cells
  table_merged_cell_ids, merged_cell_table_ids = construct_table_merged_cell_ids(table_blocks)

  # Initiliaze the Pandas dataframes
  table_ids = [table_block['Id'] for table_block in table_blocks]
  tables = {}
  for table_id in table_ids:
      tables[table_id] = pd.DataFrame()

  for line_block in line_blocks:
      # Find the element that has the CHILD type
      nn = 0
      while line_block['Relationships'][nn]['Type'] != 'CHILD':
          nn += 1
      first_word_id = line_block['Relationships'][nn]['Ids'][0] # First word id only

      # Find which cell and table this first word of the line is part of
      if first_word_id in child_cell_ids.keys():
          parent_cell_id = child_cell_ids[first_word_id]
          # Get the block corresponding to this parent cell
          cell_block = [block for block in cell_blocks if block['Id']==parent_cell_id][0]
          # Get the row and column where the word should be located
          row = cell_block['RowIndex']-1
          col = cell_block['ColumnIndex']-1
          if parent_cell_id in child_table_ids.keys():
              parent_table_id = child_table_ids[parent_cell_id]
              if (row in tables[parent_table_id].index) and (col in tables[parent_table_id].columns) and (pd.notnull(tables[parent_table_id].loc[row, col])):
                  # Add to existing content in the cell after returning the newline symbol if the cell already exists
                  tables[parent_table_id].loc[row, col] = (str(tables[parent_table_id].loc[row, col]) +
                                                           '\n' +
                                                           str(line_block['Text']))
              else:
                  # Create the cell if its does not exist
                  tables[parent_table_id].loc[row, col] = str(line_block['Text'])

  # Additional treatment for each table
  for key in tables.keys():
      # Order row and column
      tables[key] = tables[key][tables[key].columns.sort_values()]
      tables[key] = tables[key].loc[tables[key].index.sort_values()]
      # Replace NaN values by an empty string
      tables[key] = tables[key].fillna('')
      # Merge columns (concatenate strings)
      merged_cell_ids = table_merged_cell_ids[key]
      if len(merged_cell_ids)>0:
          for merged_cell_id in merged_cell_ids:
              # Get the block corresponding to this merged cell
              merged_cell_block = [block for block in merged_cell_blocks if block['Id']==merged_cell_id][0]
              if merged_cell_block['RowSpan'] == 1: # Check RowSpan is 1 (we only do merging of columns)
                  row0 = merged_cell_block['RowIndex']-1 # Get the row
                  col0 = merged_cell_block['ColumnIndex']-1 # Get the starting column index
                  colspan = merged_cell_block['ColumnSpan'] # Get the number of columns involved
                  # Build the content by concatenating the string from each column
                  content = ''
                  for jj in range(colspan):
                      content += ' ' + tables[key].loc[row0, col0+jj]
                  # Replace with the content back in the dataframe for each column
                  for jj in range(colspan):
                      tables[key].loc[row0, col0+jj] = content.strip()

  return tables