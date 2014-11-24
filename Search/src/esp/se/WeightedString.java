package esp.se;

import java.util.Comparator;

public class WeightedString {
	public String str;
	public double weight;

	public WeightedString(String str, double weight) {
		this.str = str;
		this.weight = weight;
	}

	@Override
	public String toString() {
		return "WeightedString [str=" + str + ", weight=" + weight + "]";
	}

}

class WSComparator implements Comparator<WeightedString> {

	@Override
	public int compare(WeightedString o1, WeightedString o2) {
		if (o1.weight == o2.weight)
			return 0;
		return o1.weight < o2.weight ? 1 : -1;
	}

}