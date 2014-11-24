package esp.ir;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import esp.util.Config;

public class Tokenizer {
	private static Set<String> stopwords = null;
	private static String dataPath = Config.dataPath;

	public Tokenizer() {
	}

	public static void loadStopwords() {
		stopwords = new HashSet<>();
		BufferedReader br;
		try {
			br = new BufferedReader(new InputStreamReader(new FileInputStream(
					dataPath + "stopwords")));
			String line;
			while ((line = br.readLine()) != null) {
				stopwords.add(line);
			}
			br.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static ArrayList<String> toIndexableTerms(String doc) {
		ArrayList<String> wds = new ArrayList<>();
		String[] s = doc.replaceAll("[^a-zA-Z0-9 ]", "").toLowerCase()
				.split("\\s+");
		for (String wd : s)
			if (!stopwords.contains(wd))
				wds.add(wd);
		return wds;
	}

}
