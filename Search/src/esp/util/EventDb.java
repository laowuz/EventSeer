package esp.util;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

import esp.se.Event;
import esp.se.URLInfo;

public class EventDb extends Db {
	public static final String DB_HOST = "sundance.ist.psu.edu/";
	public static final String DB_NAME = "wiki_event";
	public static final String DB_USER = "cul226";
	public static final String DB_PASSWD = "eventsearch";
	public static final String EVENT_TABLE = "wikistoriesfrom2003";
	public static final String URL_TABLE = "wikieventurls";

	public EventDb() throws ClassNotFoundException {
	}

	public void connect() throws SQLException {
		if (connect == null || connect.isClosed()) {
			connect = DriverManager.getConnection("jdbc:mysql://" + DB_HOST
					+ DB_NAME, DB_USER, DB_PASSWD);
		}
	}

	public List<Event> selectAllEvents() {
		System.out.println(Config.infoHeader + "select all events from db");
		List<Event> events = null;
		try {
			events = new ArrayList<>();
			statement = connect.createStatement();
			String sql = "select * from " + EVENT_TABLE + " order by id";
			resultSet = statement.executeQuery(sql);
			while (resultSet.next()) {
				int id = resultSet.getInt("id");
				if (resultSet.getString("before13").equals("y")) {
					if (id < 9000)
						continue;
					id += Config.offset;
				}
				String title = resultSet.getString("title");
				String content = resultSet.getString("content");
				Event e = new Event(title, resultSet.getString("date"),
						resultSet.getInt("cate"), id, content,
						resultSet.getString("urls"),
						resultSet.getString("anchs"));
				events.add(e);
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return events;
	}

	public List<URLInfo> selectURLInfo(int eid) {
		List<URLInfo> infos = null;
		try {
			infos = new ArrayList<>();
			if (connect.isClosed())
				connect();
			statement = connect.createStatement();
			String sql = "select * from " + URL_TABLE + " where eventid = "
					+ eid;
			resultSet = statement.executeQuery(sql);
			while (resultSet.next()) {
				URLInfo info = new URLInfo(resultSet.getString("date"),
						resultSet.getString("newstitle"),
						resultSet.getString("description"),
						resultSet.getString("url"), eid);
				infos.add(info);
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return infos;
	}

	public static void main(String[] args) throws Exception {
		EventDb db = new EventDb();
		db.connect();
		List<URLInfo> events = db.selectURLInfo(15);
		System.out.println(events.size());
	}

}
