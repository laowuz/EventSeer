package esp.ir;

import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import esp.se.Server;

public class Evaluation {
	public String output = "query_label";
	public Server s = Server.getInstance();
	public String[] queries = { "United States", "Russia", "China",
			"Barack Obama", "European Union", "President of the United States",
			"Car bomb", "North Korea", "South Korea", "President of Russia" };
	public String[] methods = { "bm25", "cosine", "ip" };

	public int N = 10;

	public void run() throws Exception {

		for (int i = 0; i < methods.length; i++) {
			BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(
					new FileOutputStream(output + "." + methods[i]), "utf-8"));
			for (int k = 0; k < N; k++) {
				for (String q : queries) {
					bw.write(q);
					bw.newLine();
					JSONObject res = s.queryFromDb(q, 0, 10, i, 0);
					JSONArray data = (JSONArray) res.get("data");
					bw.write("" + data.size());
					bw.newLine();
					for (int j = 0; j < data.size(); j++) {
						JSONObject e = (JSONObject) data.get(j);
						bw.write((String) e.get("title"));
						bw.newLine();
					}
				}
			}
			System.out.println(s.time / Math.pow(10, 9) / N / queries.length);
			s.time = 0;
			bw.close();
		}
	}

	public static void main(String[] args) throws Exception {
		Evaluation e = new Evaluation();
		e.run();
	}

}
