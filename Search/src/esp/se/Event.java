package esp.se;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Comparator;
import java.util.Date;
import java.util.Locale;

public class Event {
	private String title;
	private String date;
	private int category;
	private int id;
	private String content;
	private String url;
	private String anchs;
	private String[] urls;

	public Event(String title, String date, int category, int id,
			String content, String url, String anchs) {
		super();
		this.title = title;
		this.date = date;
		this.category = category;
		this.id = id;
		this.content = content;
		this.url = url;
		this.anchs = anchs;
		this.urls = url.split("\\|\\|");
	}

	public String getTitle() {
		return title;
	}

	public String getDate() {
		return date;
	}

	public int getCategory() {
		return category;
	}

	public int getId() {
		return id;
	}

	public String getContent() {
		return content;
	}

	public String getUrl() {
		return url;
	}

	public String getAnchs() {
		return anchs;
	}

	public String getDocument() {
		return title + " " + content;
	}

	public String[] getAllUrl() {
		return urls;
	}

	@Override
	public String toString() {
		return "Event [title=" + title + ", date=" + date + ", category="
				+ category + ", id=" + id + ", content=" + content + ", url="
				+ url + ", anchs=" + anchs + "]";
	}

}

class EventComparator implements Comparator<Event> {

	DateFormat format = new SimpleDateFormat("yyyy-MM-dd", Locale.ENGLISH);

	@Override
	public int compare(Event o1, Event o2) {
		if (o1.getDate() == o2.getDate())
			return 0;
		Date d1 = null, d2 = null;
		try {
			d1 = format.parse(o1.getDate());
			d2 = format.parse(o2.getDate());
		} catch (Exception e) {
			e.printStackTrace();
		}
		return d1.after(d2) ? 1 : -1;
	}
}
