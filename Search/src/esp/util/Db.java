package esp.util;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public abstract class Db {
	protected Connection connect = null;
	protected Statement statement = null;
	protected ResultSet resultSet = null;

	public Db() throws ClassNotFoundException {
		Class.forName("com.mysql.jdbc.Driver");
	}

	abstract public void connect() throws SQLException;


	public List<String> getColumnNames(String tableName) throws SQLException {
		DatabaseMetaData metaData = connect.getMetaData();
		ResultSet columns = metaData.getColumns(null, null, tableName, null);
		List<String> colname = new ArrayList<>();
		while (columns.next()) {
			colname.add(columns.getString("COLUMN_NAME"));
		}
		return colname;
	}

	protected void finalize() throws Throwable {
		disconnect();
	}

	public void disconnect() {
		try {
			connect.close();
		} catch (SQLException e) {
			// there's nothing you can do!
			e.printStackTrace();
		}
	}

}
