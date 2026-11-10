import numpy as np
from energy_transition.paper_t_v15_sector_mixture import N,IDX,TRAIN,fit_inverse,predict,score
def test_common_support_and_frozen_split():
    assert len(IDX)==8757 and IDX[0]==3 and IDX[-1]==8759
    assert TRAIN.sum()==4377 and (~TRAIN).sum()==4380
def test_inverse_sector_weights_known():
    h=np.arange(N)
    v=np.stack([200+np.sin(h/20),100+np.cos(h/15),80+np.sin(h/30),30+np.cos(h/9)])
    desired=np.array([.22,.42,.68,.87])
    full=(v[:,IDX-3].T+(v[:,IDX-2]-v[:,IDX-3]).T*desired).sum(axis=1)
    target=np.zeros(N)
    target[IDX]=full
    w=fit_inverse(target,v)
    assert np.max(np.abs(w-desired))<1e-5
    assert score(full,predict(v,w),np.ones(len(IDX),dtype=bool))["mae_mw"]<1e-7
def test_frozen_approach_does_not_wrap():
    h=np.arange(N,dtype=float)
    v=np.stack([h,h*0.2,h*0.3,h*0.5])
    y=np.zeros(N);y[IDX]=(v[:,IDX-2]*.5+v[:,IDX-3]*.5).sum(axis=0)
    result=fit_inverse(y,v)
    assert np.all(result>=0) and np.all(result<=1)
