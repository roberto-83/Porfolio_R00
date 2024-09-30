import pyarrow.parquet as pq
import numpy as np
import pandas as pd
import pyarrow as pa
import os

perc_folder = os.path.dirname(__file__)+"/ParquetFile/"
df = pd.DataFrame({'one': [-1, np.nan, 2.5],
                   'two': ['foo', 'bar', 'baz'],
                   'three': [True, False, True]},
                   index=list('abc'))
table = pa.Table.from_pandas(df)

#scrivo
#pq.write_table(table, perc_folder+'example.parquet')
#print('Dati scritti')

#leggo
table2 = pq.read_table(perc_folder+'example.parquet')

print(table2.to_pandas())

#leggo solo colonne
col=pq.read_table(perc_folder+'example.parquet', columns=['one', 'three'])
print(col)
#Leggo direttamente su pandas
col2=pq.read_pandas(perc_folder+'example.parquet', columns=['two']).to_pandas()
print(col2)