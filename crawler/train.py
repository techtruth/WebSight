#!/usr/bin/python3
###
# Given a list of url with content, 
#  train a Top2Vec model
#  and export its data
#  in a somoclu-friendly format
###

from top2vec import Top2Vec
import pickle
import somoclu
import numpy as np

def train_top2vec(preprocessed_data):
  tagged_documents = [page["content"] for page in preprocessed_data]
  id_documents = [page["url"] for page in preprocessed_data]
  print("Organized data...")
  model = Top2Vec(documents=tagged_documents,
                  document_ids=id_documents, 
                  min_count=1,
                  keep_documents=False,
                  speed='fast-learn', 
                  workers=19, 
                  embedding_model="doc2vec", 
                  use_corpus_file=True )

  print("Caching Doc2Vec data to disk...")
  with open('cache.top2vec', 'wb') as file:
      pickle.dump(model, file)
      print('Doc2Vec object written to cache')
  print("Doc2Vec model created.")
  save_somoclu_format(id_documents, model)
  return model

def train_somoclu(namefile, lrnfile):
    print("LOLOLOL")
    som = somoclu.Somoclu(verbose=2,
                          n_columns=256, 
                          n_rows=256, 
                          kerneltype=1, 
                          maptype='planar', 
                          gridtype='rectangular', 
                          neighborhood='gaussian', 
                          compactsupport=False )

    with open("input.somoclu.docvec.lrn", 'r') as docvec_file:
      docvec = []
      next(docvec_file)
      next(docvec_file)
      next(docvec_file)
      next(docvec_file)
      for vector_line in docvec_file:
          docvec.append(vector_line.split()[1:])
    
      docvec_np = np.array(docvec, dtype=np.float32);
      print(docvec_np, docvec_np.shape)

    som.train(data=docvec_np,
              epochs=256,
              radiuscooling="exponential")

    #Codebook
    with open("somoclu.codebook", 'wb') as f:
      f.write(som.codebook)
    #BMU
    with open("somoclu.bmu", 'wb') as f:
      f.write(som.bmus)
    #UMatrix
    with open("somoclu.umatrix", 'wb') as f:
      f.write(som.umatrix)

def save_somoclu_format(names, model):
  ##Convert Doc2Vec into somoclu input format 
  with open("input.somoclu.names", 'w') as f:
    f.write("% " + str(len(names)) + '\n') #Header
    for index, tag in enumerate(names):
        f.write(str(index) + ' ')
        f.write(str(tag) + ' ')
        f.write(str(tag) + '\n')
        
  #Save topic words
  topic_words = model.topic_words
  with open("topics.txt", 'w') as f:
      for tag in range(len(topic_words)):
          line = str(tag) + "\t"
          line += ' '.join([str(dim) for dim in topic_words[tag]])
          f.write(line + '\n')
   
  #Save topic vectors
  topic_vectors = model.topic_vectors
  with open("input.somoclu.topvec.lrn", 'w') as f:
      f.write("% " + str(len(topic_vectors)) + '\n') #Rows
      f.write("% " + str(len(topic_vectors[0])) + '\n') #Columns
      f.write("% " + "9")
      for i in range(len(topic_vectors[0])):
          f.write(" " + str(1))
      f.write('\n') # Training Mask
      f.write("% " + "Ignore me please!" + '\n') # Variable names (ignored)
      for tag in range(len(topic_vectors)):
          line = str(tag) + "\t"
          line += ' '.join([str(dim) for dim in topic_vectors[tag]])
          f.write(line + '\n')
   
  document_vectors = model.document_vectors
  with open("input.somoclu.docvec.lrn", 'w') as f:
      f.write("% " + str(len(document_vectors)) + '\n') #Rows
      f.write("% " + str(len(document_vectors[0])) + '\n') #Columns
      f.write("% " + "9")
      for i in range(len(document_vectors[0])):
          f.write(" " + str(1))
      f.write('\n') # Training Mask
      f.write("% " + "Ignore me please!" + '\n') # Variable names (ignored)
      for tag in range(len(document_vectors)):
          line = str(tag) + "\t"
          line += ' '.join([str(dim) for dim in document_vectors[tag]])
          f.write(line + '\n')     
