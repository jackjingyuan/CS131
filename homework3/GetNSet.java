import java.util.concurrent.atomic.AtomicIntegerArray;

class GetNSet implements State {
    private byte maxval;
    private AtomicIntegerArray Aarray;

	private void createAtomicArray(byte[] v){
    	int[] intArray = new int[v.length];
    	for(int i = 0; i < v.length; i++){
    		intArray[i] = v[i];
		}
		Aarray = new AtomicIntegerArray(intArray);
	}


    GetNSet(byte[] v) { 
    	maxval = 127;
    	createAtomicArray(v);
    }

    GetNSet(byte[] v, byte m) { 
    	maxval = m;
    	createAtomicArray(v);
    }

    public int size() { return Aarray.length(); }

    public byte[] current() { 
		byte[] a = new byte[Aarray.length()];
		for(int i = 0; i < a.length; i++){
			a[i] = (byte) Aarray.get(i);
		}
		return a;
	}

	public boolean swap(int i, int j) {
		if (Aarray.get(i) <= 0 || Aarray.get(j) >= maxval) {
			return false;
		}
		Aarray.getAndDecrement(i);
		Aarray.getAndIncrement(j);
		return true;
	}
}
