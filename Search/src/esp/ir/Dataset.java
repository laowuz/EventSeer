package esp.ir;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import esp.se.Event;
import esp.util.Config;
import esp.util.EventDb;

public class Dataset {
	public List<Event> events = null;
	public HashMap<String, ArrayList<Integer>> title2event = null;
	public EventDb eventDb = null;
	public List<Doc> docs = null;

	public Dataset() {
		try {
			eventDb = new EventDb();
			eventDb.connect();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void load() {
		events = eventDb.selectAllEvents();
		// build event index
		title2event = new HashMap<String, ArrayList<Integer>>();
		for (int i = 0; i < events.size(); i++) {
			Event e = events.get(i);
			String title = e.getTitle();
			if (!title2event.containsKey(title))
				title2event.put(title, new ArrayList<Integer>());
			title2event.get(title).add(i);
		}
		System.out.println(Config.infoHeader + "building event index done");
		docs = new ArrayList<>();
		for (String title : title2event.keySet()) {
			StringBuilder sb = new StringBuilder();
			ArrayList<Integer> idxs = title2event.get(title);
			for (int idx : idxs)
				sb.append(events.get(idx).getContent() + ' ');
			docs.add(new Doc(title, sb.toString(), idxs));
		}
	}

	public static void main(String[] args) {
		Dataset d = new Dataset();
		d.load();

	}

}
