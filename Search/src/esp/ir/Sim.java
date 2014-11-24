package esp.ir;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

public class Sim {
	public static HashMap<String, Integer> df = null;
	public static int N = -1;
	private static double k1 = 1.5; // BM25
	private static double b = 0.75; // BM25
	private static double avgdl = 0;

	public static void init(HashMap<String, Integer> df_tmp, int N_tmp,
			double avgdl_tmp) {
		df = df_tmp;
		N = N_tmp;
		avgdl = avgdl_tmp;
	}

	public static double cosineSimilarity(String query, String doc) {
		double cos = 0;
		HashMap<String, Double> qVec = tfidf(query);
		HashMap<String, Double> dVec = tfidf(doc);
		double lq = 0, ld = 0;
		for (String wd : qVec.keySet()) {
			double qVal = qVec.get(wd);
			if (dVec.containsKey(wd))
				cos += qVal * dVec.get(wd);
			lq += qVal * qVal;
		}
		for (String wd : dVec.keySet()) {
			double dVal = dVec.get(wd);
			ld += dVal * dVal;
		}

		cos = cos / (Math.sqrt(lq) * Math.sqrt(ld));

		return cos;
	}

	public static double innerProduct(String query, String doc) {
		double ip = 0;
		HashMap<String, Double> qVec = tfidf(query);
		HashMap<String, Double> dVec = tfidf(doc);
		for (String wd : qVec.keySet()) {
			double qVal = qVec.get(wd);
			if (dVec.containsKey(wd))
				ip += qVal * dVec.get(wd);
		}
		return ip;
	}

	public static HashMap<String, Double> tfidf(String doc) {
		HashMap<String, Double> tfidf = new HashMap<>();
		ArrayList<String> words = Tokenizer.toIndexableTerms(doc);
		HashMap<String, Integer> tf = new HashMap<>();
		for (String wd : words) {
			if (tf.containsKey(wd))
				tf.put(wd, tf.get(wd) + 1);
			else
				tf.put(wd, 1);
		}

		for (String wd : words) {
			double tfidf_score = 0;
			if (df.containsKey(wd))
				tfidf_score = tf.get(wd)
						* (Math.log((double) N / df.get(wd)) + 1);
			tfidf.put(wd, tfidf_score);
		}
		return tfidf;
	}

	public static double bm25(String query, String doc) {
		double score = 0;
		ArrayList<String> qWds = Tokenizer.toIndexableTerms(query);
		HashSet<String> qSets = new HashSet<>(qWds);
		ArrayList<String> dWds = Tokenizer.toIndexableTerms(doc);

		// calculate f(q,D)
		HashMap<String, Integer> f = new HashMap<>();
		for (String q : qSets)
			f.put(q, 0);
		for (String wd : dWds) {
			if (qSets.contains(wd)) {
				f.put(wd, f.get(wd) + 1);
			}
		}
		int D = dWds.size();
		for (String q : qWds) {
			if (df.containsKey(q))
				score += idf_bm25(q) * f.get(q) * (k1 + 1)
						/ (f.get(q) + k1 * (1 - b + b * D / avgdl));
		}
		return score;
	}

	public static double test(String query, String doc) {
		double score = 0;
		ArrayList<String> qWds = Tokenizer.toIndexableTerms(query);
		HashSet<String> qSets = new HashSet<>(qWds);
		ArrayList<String> dWds = Tokenizer.toIndexableTerms(doc);

		// calculate f(q,D)
		HashMap<String, Integer> f = new HashMap<>();
		for (String q : qSets)
			f.put(q, 0);
		for (String wd : dWds) {
			if (qSets.contains(wd)) {
				f.put(wd, f.get(wd) + 1);
			}
		}
		int D = dWds.size();
		for (String q : qWds) {
			if (df.containsKey(q))
				score += idf_bm25(q) * f.get(q) * (k1 + 1)
						/ (f.get(q) + k1 * (1 - b + b * avgdl / Math.log(D)));
		}
		return score;
	}

	private static double idf_bm25(String q) {
		double score = Math.log((N - df.get(q) + 0.5) / (df.get(q) + 0.5));
		return score;
	}

}
