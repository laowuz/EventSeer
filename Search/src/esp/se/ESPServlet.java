package esp.se;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.net.URLEncoder;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

@WebServlet("/ESPServlet")
public class ESPServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	private Server server = Server.getInstance();

	private static String baseUrl = "/esp/ESPServlet";
	private static int PAGE_SIZE = 10;
	private static int BLOCK_NUM = 4;
	private static final int TYPE_QUERY = 0;
	private static final int TYPE_EVENT = 1;
	private static final int TYPE_STORY = 2;
	private final String[] methodNames = { "BM25", "Cosine", "Inner product",
			"test" };
	private final String[] sortNames = { "Relevance", "Popularity", "Recency" };
	private final String[] cats = { "conflict/attack", "disaster/accident",
			"international relations", "politics/elections", "law/crime",
			"economy/business", "science/technology", "sports", "arts/culture",
			"health/environment", "education", "deaths" };
	private final int[] css = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 };

	public ESPServlet() {
		super();
	}

	protected void doGet(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		String query = request.getParameter("q");
		String eid = request.getParameter("e");
		String title = request.getParameter("t");
		String pageStr = request.getParameter("page");

		String methodStr = request.getParameter("m");
		String sortStr = request.getParameter("sort");
		int pageNum = 0;
		if (pageStr != null)
			pageNum = Integer.valueOf(pageStr);
		int sort = 0;
		if (sortStr != null)
			sort = Integer.valueOf(sortStr);
		int method = 0;
		if (methodStr != null)
			method = Integer.valueOf(methodStr);

		System.out.println("doGet()");
		System.out.println("query = " + query);
		System.out.println("eid = " + eid);
		System.out.println("story title = " + title);

		System.out.println("pageNum = " + pageNum);
		response.setContentType("text/html;charset=UTF-8");
		PrintWriter out = response.getWriter();

		String template = null;
		if (query != null) {
			query = URLDecoder.decode(query, "utf-8");
			template = generateResultsTemplate(query, pageNum, method, sort);
		}
		if (eid != null)
			template = generateEventUrlsTemplate(eid, pageNum);
		if (title != null) {
			title = URLDecoder.decode(title, "utf-8");
			template = generateStoryTemplate(title, pageNum);
		}

		out.print(template);
	}

	private String generateStoryTemplate(String title, int pageNum)
			throws UnsupportedEncodingException {
		System.out.println("generateStoryTemplate : " + title + " " + pageNum);
		String template = server.getResultTemplate();
		JSONObject res = server.getStoryFromDb(title, pageNum, PAGE_SIZE);
		int totRes = (int) res.get("tot");
		int totPage = totRes / 10;
		if (totRes % 10 != 0)
			totPage++;

		JSONArray data = (JSONArray) res.get("data");
		String encode_title = URLEncoder.encode(title, "UTF-8").replace("+",
				"%20");
		String wikiUrl = "http://en.wikipedia.org/wiki/" + encode_title;
		String titleHtml = "<div> <h3> <a href=\"" + wikiUrl + "\">" + title
				+ "</a></h3></div>";

		String resultHtml = getStoryHtml(data, totRes);
		String pagesHtml = getPagesHtml(totPage, pageNum, TYPE_STORY, title);

		template = template.replace("#value#", "");
		template = template.replace("#method#", "");
		template = template.replace("#sort#", "");
		template = template.replace("#result#", titleHtml + resultHtml);
		template = template.replace("#pages#", pagesHtml);
		return template;
	}

	private String getStoryHtml(JSONArray res, int tot) {
		String html = "<div class=\"resNum\"> Total <strong>" + tot
				+ "</strong> events </div>";
		for (int i = 0; i < res.size(); i++) {
			html += "<div class= \"result\">";
			JSONObject jo = (JSONObject) res.get(i);
			String url = baseUrl + "?e=" + jo.get("id");
			html += "<blockquote><p> " + jo.get("content") + " <a href = \""
					+ url + "\"> more</a>" + "</p></blockquote>";

			html += "<div class=\"text-right\">";
			int cat = (int) jo.get("category");
			if (cat != 0) {
				html += "<span class=\"label label-color-" + css[cat - 1]
						+ "\">" + cats[cat - 1] + "</span>";
			}
			html += "<span class=\"event_date\"> <em>" + jo.get("date")
					+ "</em></span>";
			html += "</div>";
			html += "</div>";
		}
		return html;
	}

	private String generateEventUrlsTemplate(String eid, int pageNum)
			throws UnsupportedEncodingException {
		String template = server.getResultTemplate();
		JSONObject res = server.getEventFromDb(eid, pageNum, PAGE_SIZE);
		int totRes = (int) res.get("tot");
		int totPage = totRes / 10;
		if (totRes % 10 != 0)
			totPage++;
		String desc = (String) res.get("content");
		String descHtml = "<blockquote><p>" + desc + "</p></blockquote>";
		JSONArray data = (JSONArray) res.get("data");
		String resultHtml = getEventHtml(data, totRes);
		String pagesHtml = getPagesHtml(totPage, pageNum, TYPE_EVENT, eid);

		template = template.replace("#value#", "");
		template = template.replace("#method#", "");
		template = template.replace("#sort#", "");
		template = template.replace("#result#", descHtml + resultHtml);
		template = template.replace("#pages#", pagesHtml);

		return template;
	}

	private String generateResultsTemplate(String query, int pageNum,
			int methodType, int sortType) throws UnsupportedEncodingException {
		System.out.println("generateResultsTemplate:" + query + ' ' + pageNum
				+ ' ' + methodType + ' ' + sortType);
		JSONObject res = server.queryFromDb(query, pageNum, PAGE_SIZE,
				methodType, sortType);
		int totRes = (int) res.get("tot");
		int totPage = totRes / 10;
		if (totRes % 10 != 0)
			totPage++;

		String template = server.getResultTemplate();
		template = template.replace("#value#", query);

		JSONArray data = (JSONArray) res.get("data");
		query = URLEncoder.encode(query, "utf-8");
		String methodUrl = baseUrl + "?q=" + query + "&m=";
		String methodHtml = getDropDownHtml(methodUrl, "Method:", methodType,
				methodNames);
		String sortUrl = methodUrl + methodType + "&sort=";
		String sortHtml = getDropDownHtml(sortUrl, "Sorted by", sortType,
				sortNames);
		String resultHtml = getResultHtml(data, totRes);
		String pagesHtml = getPagesHtml(totPage, pageNum, TYPE_QUERY, query);

		template = template.replace("#method#", methodHtml);
		template = template.replace("#sort#", sortHtml);
		template = template.replace("#result#", resultHtml);
		template = template.replace("#pages#", pagesHtml);
		return template;
	}

	private String getDropDownHtml(String url, String text, int curNo,
			String[] names) {
		String html = "<ul class=\"nav navbar-nav navbar-left\">";
		html += "<div class=\"navbar-text\">" + text + "</div>";
		html += "<li class=\"dropdown\"><a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\">"
				+ names[curNo] + "<b class=\"caret\"> </b></a>";
		html += "<ul class = \"dropdown-menu\">";
		for (int i = 0; i < names.length; i++)
			html += "<li><a href=\"" + url + i + "\">" + names[i] + "</a></li>";
		html += "</ul></li>";
		html += "</ul>";
		return html;
	}

	private String getEventHtml(JSONArray res, int tot) {
		String html = "<div class=\"resNum\"> Total <strong>" + tot
				+ "</strong> news articles </div>";
		for (int i = 0; i < res.size(); i++) {
			html += "<div class= \"result\">";
			JSONObject jo = (JSONObject) res.get(i);
			String title = (String) jo.get("title");
			if (title == null)
				title = "default title";
			html += "<div class=\"result_title\">" + "<h4> <a href=\""
					+ jo.get("url") + "\" >" + title + " </a></h4></div>";
			html += "<div class=\"desc_bar\">";
			html += "<span class=\"news_date\">" + jo.get("date") + "</span>";
			html += "<span class=\"news_hyphen\"> - </span>";
			html += "<span class=\"result_url\">" + jo.get("url") + "</span>";
			html += "</div>";
			String description = (String) jo.get("description");
			if (description != null) {
				description = server.trimContent(description, 300);
				html += "<div class=\"reslt_description\">" + description
						+ "</div>";
			}
			html += "</div>";
		}
		return html;
	}

	private String getResultHtml(JSONArray res, int tot)
			throws UnsupportedEncodingException {
		String html = "<div class=\"resNum\"> Total <strong>" + tot
				+ "</strong> results </div>";

		for (int i = 0; i < res.size(); i++) {
			html += "<div class= \"result\">";
			JSONObject jo = (JSONObject) res.get(i);
			String title = (String) jo.get("title");
			title = URLEncoder.encode(title, "utf-8");
			System.out.println("title after encode: " + title);
			String titleUrl = baseUrl + "?t=" + title;
			html += "<div class=\"result_title\">" + "<h4> <a href=\""
					+ titleUrl + "\">" + jo.get("title") + " </a></h4></div>";

			JSONArray ja = (JSONArray) jo.get("events");

			html += "<div class=\"event_num\">" + ja.size() + " events </div>";
			int size = Math.min(BLOCK_NUM, ja.size());
			int[] sample = new int[size];
			for (int j = 0; j < size; j++) {
				if (ja.size() > BLOCK_NUM)
					sample[j] = (ja.size() - 1) * j / (BLOCK_NUM - 1);
				else
					sample[j] = j;
			}

			html += "<div class=\"row\">";
			for (int j = 0; j < size; j++) {
				JSONObject eventJo = (JSONObject) ja.get(sample[j]);
				html += "<div class=\"col-md-3 block_margin\">";
				html += "<div>" + eventJo.get("content") + "</div>";
				String url = baseUrl + "?e=" + eventJo.get("id");
				html += "<a href = \"" + url + "\"> more</a>";
				html += "<div class=\"text-right\">";
				int cat = (int) eventJo.get("category");
				if (cat != 0) {
					html += "<span class=\"label label-color-" + css[cat - 1]
							+ "\">" + cats[cat - 1] + "</span>";
				}
				html += "<span class=\"event_date\"> <em>"
						+ eventJo.get("date") + "</em></span>";
				html += "</div>";
				html += "</div>";
			}
			html += "</div>";
			html += "</div>";
		}
		return html;
	}

	private String getPagesHtml(int totPage, int curPage, int qType,
			String query) throws UnsupportedEncodingException {
		query = URLEncoder.encode(query, "utf-8");
		String html = "";
		String url = null;

		switch (qType) {
		case TYPE_EVENT:
			url = baseUrl + "?e=" + query;
			break;
		case TYPE_STORY:
			url = baseUrl + "?t=" + query;
			break;
		case TYPE_QUERY:
			url = baseUrl + "?q=" + query;
			break;
		default:
			break;
		}

		html += "<ul class= \"pagination\"> \n";
		// prev
		if (curPage > 0)
			html += getPaginationListItem("", url + "&page=" + (curPage - 1),
					"&laquo;");
		else
			html += getPaginationListItem("disabled", "#", "&laquo;");
		int minIdx = Math.max(0, curPage - PAGE_SIZE / 2);
		int maxIdx = Math.min(curPage + PAGE_SIZE / 2 - 1, totPage - 1);
		if (minIdx == 0)
			maxIdx = Math.min(PAGE_SIZE - 1, totPage - 1);
		if (maxIdx == totPage - 1)
			minIdx = Math.max(0, totPage - PAGE_SIZE);
		for (int i = minIdx; i < maxIdx + 1; i++) {
			if (i == curPage)
				html += getPaginationListItem("active", "#", "" + (i + 1));
			else
				html += getPaginationListItem("", url + "&page=" + i, ""
						+ (i + 1));
		}

		// next
		if (curPage < totPage - 1)
			html += getPaginationListItem("", url + "&page=" + (curPage + 1),
					"&raquo;");
		else
			html += getPaginationListItem("disabled", "#", "&raquo;");
		html += "</ul> \n";
		return html;
	}

	private String getPaginationListItem(String li_class, String ahref,
			String label) {
		String listItem = "<li";
		if (li_class.length() > 0)
			listItem += " class=\"" + li_class + "\"";
		listItem += "><a href = \"" + ahref + "\"> " + label + "</a></li>"
				+ "\n";
		return listItem;
	}
}
