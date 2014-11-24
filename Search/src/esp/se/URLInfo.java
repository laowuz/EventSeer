package esp.se;

public class URLInfo {
	private String date;
	private String title;
	private String description;
	private String url;
	private int id;

	public URLInfo(String date, String title, String description, String url,
			int id) {
		super();
		this.date = date;
		this.title = title;
		this.description = description;
		this.url = url;
		this.id = id;
	}

	public String getDate() {
		return date;
	}

	public String getTitle() {
		return title;
	}

	public String getDescription() {
		return description;
	}

	public String getUrl() {
		return url;
	}

	public int getId() {
		return id;
	}

}
