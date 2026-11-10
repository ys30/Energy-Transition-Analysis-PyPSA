import numpy as np
from energy_transition.paper_t_idaho_bidirectional_residual import align,weights,metrics,N
def test_offset_support_and_reverse_orientation():
    x=np.arange(N,dtype=float)
    i,y,X=align(x,x,(-2,-3))
    assert len(i)==N-3 and X[0].tolist()==[2,3]
    j,z,Y=align(x,x,(2,3))
    assert len(j)==N-3 and Y[0].tolist()==[1,0]
def test_simplex_known_weight():
    x=2000+100*np.sin(np.arange(N)*.13)
    y=.82*np.roll(x,-2)+.18*np.roll(x,-3)
    i,target,X=align(y,x,(-2,-3))
    assert np.allclose(weights(target,X),[.82,.18],atol=1e-5)
def test_expanded_components_and_error():
    x=2000+100*np.sin(np.arange(N)*.13)
    y=.3*np.roll(x,-1)+.7*np.roll(x,-4)
    i,target,X=align(y,x,(-1,-2,-3,-4))
    assert np.allclose(weights(target,X)@np.ones(4),1)
    assert metrics(target,X@weights(target,X))["mae_mw"]<.01
