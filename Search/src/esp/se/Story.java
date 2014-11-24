package esp.se;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Comparator;
import java.util.Date;
import java.util.Locale;

public class Story {
	public String title;
	public double score;
	public int eventNum;
	public String recentDate;

	@Override
	public String toString() {
		return "Story [title=" + title + ", score=" + score + ", eventsNum="
				+ eventNum + ", recentDate=" + recentDate + "]";
	}

	public Story(String title, double score, int eventsNum, String recentDate) {
		super();
		this.title = title;
		this.score = score;
		this.eventNum = eventsNum;
		this.recentDate = recentDate;
	}

}

class StoryComparator implements Comparator<Story> {
	int type;
	DateFormat format;

	public StoryComparator(int type) {
		this.type = type;
		this.format = new SimpleDateFormat("yyyy-MM-dd", Locale.ENGLISH);
	}

	@Override
	public int compare(Story o1, Story o2) {
		if (type == 0) {
			if (o1.score == o2.score)
				return 0;
			return o1.score < o2.score ? 1 : -1;
		} else if (type == 1) {
			if (o1.eventNum == o2.eventNum)
				return 0;
			return o1.eventNum < o2.eventNum ? 1 : -1;
		} else if (type == 2) {
			if (o1.recentDate == o2.recentDate)
				return 0;
			Date d1 = null, d2 = null;
			try {
				d1 = format.parse(o1.recentDate);
				d2 = format.parse(o2.recentDate);
			} catch (Exception e) {
				e.printStackTrace();
			}
			return d1.before(d2) ? 1 : -1;
		}
		return 0;
	}
}