import uproot
import numpy as np
import matplotlib.pyplot as plt
import awkward as ak

# Open the file and get the tree
# file = uproot.open("pythia_for_full_sim.picoDst.root")
# if "PicoDst" not in file:
#     raise ValueError("PicoDst not found in the file")
# tree = file["PicoDst"]
# fwdTracks = tree["FwdTracks"]

def gen_get( fromObj:any, key:any) -> any:
    return fromObj[key]

def plot_from_tree( branch:any, leaf_name:str, nbins:int=-1, range:tuple[float,float]=None):
    leaf = branch.arrays( [leaf_name], library="ak")
    all_leaf = ak.flatten(leaf[leaf_name]).to_numpy()
    calcnbins = smartBinning(all_leaf)
    if nbins == -1:
        nbins = calcnbins
    plt.hist( all_leaf , bins=nbins, range=range)
    plt.xlabel(leaf_name)
    plt.ylabel("Counts")
    plt.title(leaf_name)

    # set log y if difference between max and min is large
    
    if np.max(all_leaf) / max( np.min(all_leaf), 0.01 ) > 100:
        plt.yscale('log')

    plt.show()

def filterLeaves( leafs:any, filter:str) -> any:
    leafs = [ x for x in leafs if filter in x]
    return leafs

def excludeFilter( leafs:any, filter:str) -> any:
    leafs = [ x for x in leafs if filter not in x]
    return leafs

# leafs = filterLeaves( fwdTracks.keys(), "FwdTracks")
# leafs = excludeFilter( leafs, "MatchIndex")
# print(leafs)

def smartBinning( array, reduced=10. ) -> int:
    # if all values are integers then return the number of unique values
    if np.all( array == np.round(array) ):
        # something weird happening with types
        minmax = int(np.max(array)) - int(np.min(array))
        minmax = minmax + 1
        lenb = len( np.unique(array) )
        
        n = max(minmax, lenb );
        n = max( n, 500 ) #dont allow more than 500 bins
        return 
        # return len( np.unique(array) )
    return len( np.unique(array) / reduced )  

def plot_foreach( branch:any, leafs:any, range:any=None):
    for leaf in leafs:
        plot_from_tree( branch, leaf, range=range)

# for leaf in leafs:
#     plot_from_tree( fwdTracks, leaf, range=None)


# print(fwdTracks["FwdTracks.mNumberOfSeedPoints"].reshape(-1))

