## INFO ##
## INFO ##


# Check if dependencies are already installed
python3 -c "from dagger.graph import Graph"
python3 -c "from orderedset import OrderedSet"

# If not
mkdir external
cd external

git clone https://github.com/petervaro/dagger
cd dagger
sudo python3 setup.py install

git clone https://github.com/petervaro/orderedset
cd orderedset
sudo python3 setup.py install

# Get back
cd ../../

# Install this
sudo python3 setup.py install
