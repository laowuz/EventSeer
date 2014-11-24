package esp.se;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.sql.SQLException;
import java.text.ParseException;
import java.util.Collections;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import esp.ir.Sim;
import esp.ir.Tokenizer;
import esp.util.Config;
import esp.util.EventDb;

public class Server {
	private static Server instance = null;
	private String resultTemplate = null;

	private static EventDb eventDb = null;
	private static String resultTemplatePath = Config.resultTemplatePath;

	private HashMap<String, ArrayList<Integer>> idx = null;
	private List<Event> data = null;

	private static HashMap<String, Integer> df = null;
	private HashMap<Integer, Integer> id2event = null;
	private static final int RESULTS_CONTENT_LENGTH = 100;
	private double avgdl = 0;

	public long time = 0;

	protected Server() {

	}

	public static Server getInstance() {
		try {
			if (instance == null) {
				instance = new Server();
				eventDb = new EventDb();
				instance.init();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return instance;
	}

	private void init() throws SQLException, UnsupportedEncodingException {
		loadResultTemplate();
		Tokenizer.loadStopwords();
		fetchDataFromDb();
		calDf();
		Sim.init(df, idx.size(), avgdl);
	}

	@SuppressWarnings("unchecked")
	public JSONObject queryFromDb(String query, int pageNum, int pageSize,
			int methodType, int sortType) {
		long stime = System.nanoTime();
		List<Story> results = new ArrayList<>();
		// rank
		for (String title : idx.keySet()) {
			StringBuilder content = new StringBuilder();
			for (int id : idx.get(title)) {
				content.append(data.get(id).getContent() + ' ');
			}
			String doc = content.append(title).toString();
			double score = 0;
			if (methodType == 0)
				score = Sim.bm25(query, doc);
			else if (methodType == 1) {
				score = Sim.cosineSimilarity(query, doc);
			} else if (methodType == 2) {
				score = Sim.innerProduct(query, doc);
			} else if (methodType == 3) {
				score = Sim.test(query, doc);
			}

			if (score > 0) {
				int eventNum = idx.get(title).size();
				results.add(new Story(title, score, eventNum, data.get(
						idx.get(title).get(eventNum - 1)).getDate()));
			}
		}
		Collections.sort(results, new StoryComparator(0));
		long etime = System.nanoTime();
		time += etime - stime;

		// re-rank
		if (sortType != 0) {
			int len = Math.min(results.size(), 10);
			Collections.sort(results.subList(0, len), new StoryComparator(
					sortType));
		}

		JSONObject res = new JSONObject();
		int tot = results.size();
		res.put("tot", tot);
		JSONArray ja = new JSONArray();
		int st = pageNum * pageSize;
		int ed = Math.min(tot - 1, st + pageSize - 1);
		for (int i = st; i < ed + 1; i++) {
			String title = results.get(i).title;
			JSONObject singleResultJo = new JSONObject();
			singleResultJo.put("title", title);
			JSONArray eventsJa = new JSONArray();

			for (int id : idx.get(title)) {
				Event e = data.get(id);
				JSONObject eventJo = new JSONObject();
				eventJo.put("date", e.getDate());
				String content = trimContent((String) e.getContent(),
						RESULTS_CONTENT_LENGTH);
				eventJo.put("content", content);
				eventJo.put("category", e.getCategory());
				eventJo.put("id", e.getId());
				eventsJa.add(eventJo);
			}
			singleResultJo.put("events", eventsJa);
			ja.add(singleResultJo);
		}
		res.put("data", ja);
		return res;
	}

	@SuppressWarnings("unchecked")
	public JSONObject getEventFromDb(String eidStr, int pageNum, int pageSize) {
		JSONObject res = new JSONObject();
		int eid = Integer.valueOf(eidStr);
		List<URLInfo> infos = null;
		if (eid < Config.offset)
			infos = eventDb.selectURLInfo(eid);
		else {
			infos = eventDb.selectURLInfo(eid - Config.offset + 100000000);
			if (infos.size() == 0)
				infos = selectBefore13(eid);
		}

		int tot = infos.size();
		res.put("tot", tot);
		Event e = data.get(id2event.get(eid));
		res.put("content", e.getContent());
		JSONArray ja = new JSONArray();
		int st = pageNum * pageSize;
		int ed = Math.min(tot - 1, st + pageSize - 1);
		for (int i = st; i < ed + 1; i++) {
			JSONObject result_jo = new JSONObject();
			URLInfo info = infos.get(i);
			result_jo.put("title", info.getTitle());
			result_jo.put("url", info.getUrl());
			result_jo.put("description", info.getDescription());
			result_jo.put("date", info.getDate());
			ja.add(result_jo);
		}
		res.put("data", ja);
		return res;
	}

	private List<URLInfo> selectBefore13(int eid) {
		List<URLInfo> infos = new ArrayList<>();
		Event e = data.get(id2event.get(Integer.valueOf(eid)));
		String[] urls = e.getAllUrl();
		String date = e.getDate();
		for (String url : urls) {
			infos.add(new URLInfo(date, null, null, url, eid));
		}
		return infos;
	}

	@SuppressWarnings("unchecked")
	public JSONObject getStoryFromDb(String title, int pageNum, int pageSize) {
		JSONObject res = new JSONObject();

		ArrayList<Integer> indexList = new ArrayList<>();
		if (idx.containsKey(title))
			indexList = idx.get(title);
		int tot = indexList.size();
		res.put("tot", tot);
		JSONArray ja = new JSONArray();
		int st = pageNum * pageSize;
		int ed = Math.min(tot - 1, st + pageSize - 1);
		for (int i = st; i < ed + 1; i++) {
			Event e = data.get(indexList.get(i));
			JSONObject event_jo = new JSONObject();
			event_jo.put("date", e.getDate());

			String content = (String) e.getContent();
			event_jo.put("content", content);
			event_jo.put("category", e.getCategory());
			event_jo.put("id", e.getId());
			ja.add(event_jo);
		}
		res.put("data", ja);
		return res;
	}

	public static String trimContent(String content, int max_length) {
		if (content.length() > max_length) {
			content = content.substring(0, content.substring(0, max_length)
					.lastIndexOf(' '))
					+ "...";
		}
		return content;
	}

	private void loadResultTemplate() {
		String html = "";
		BufferedReader br;
		try {
			br = new BufferedReader(new InputStreamReader(new FileInputStream(
					resultTemplatePath)));
			String line;
			while ((line = br.readLine()) != null) {
				html += line + '\n';
			}
			br.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		resultTemplate = html;
	}

	private void calDf() {
		System.out.println("Calculating df");
		df = new HashMap<>();
		int totdl = 0;
		for (String title : idx.keySet()) {
			StringBuilder content = new StringBuilder("");
			for (int id : idx.get(title)) {
				content.append(data.get(id).getContent() + " ");
			}
			String doc = content.append(title).toString();
			ArrayList<String> words = Tokenizer.toIndexableTerms(doc);
			totdl += words.size();
			Set<String> flag = new HashSet<>();
			for (String wd : words) {
				if (!flag.contains(wd)) {
					flag.add(wd);
					if (df.containsKey(wd))
						df.put(wd, df.get(wd) + 1);
					else
						df.put(wd, 1);
				}
			}
		}
		avgdl = (double) totdl / idx.size();
		System.out.println(idx.size());
		System.out.println(avgdl);
		System.out.println("Calculate df done");
	}

	private void fetchDataFromDb() throws SQLException,
			UnsupportedEncodingException {
		System.out.println("fetchDataFromDb()");
		eventDb.connect();
		idx = new HashMap<>();
		id2event = new HashMap<>();
		data = eventDb.selectAllEvents();
		Collections.sort(data, new EventComparator());
		int size = data.size();
		for (int i = 0; i < size; i++) {
			Event e = data.get(i);
			String title = e.getTitle();
			if (!idx.containsKey(title))
				idx.put(title, new ArrayList<Integer>());
			idx.get(title).add(i);
			int id = e.getId();
			id2event.put(id, i);
		}
	}

	public String getResultTemplate() {
		return resultTemplate;
	}

	public static void main(String[] args) throws ParseException {
		// Server s = Server.getInstance();
		// System.out.println(s.queryFromDb("Syria", 0, 10, 0, 0).toString());
		String a = "\"\"";
		System.out.println(a);
		System.out.println(a.replaceAll("\\\"", "\\\\\""));
	}
}
