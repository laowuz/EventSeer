package esp.ir;

import java.util.ArrayList;

public class Doc {
	public String title;
	public String content;
	public ArrayList<Integer> events;

	public Doc(String title, String content, ArrayList<Integer> events) {
		super();
		this.title = title;
		this.content = content;
		this.events = events;
	}
	
}
