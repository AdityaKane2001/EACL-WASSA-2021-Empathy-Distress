#Download and save word vectors
wget -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
gzip -d GoogleNews-vectors-negative300.bin.gz
mv GoogleNews-vectors-negative300.bin ../GoogleNews-vectors-negative300.bin

pip install --upgrade simpletransformers
pip install --upgrade autocorrect