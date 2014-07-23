	<table border=1>
		<tr>
			<td bgcolor=lightgray>
				Items in Pack
			</td>
			<td bgcolor=lightgray>
				Items Equiped
			</td>
			<td bgcolor=lightgray>
				Money
			</td>
		</tr>
		<tr>
			<td>
				<ul>
					{% for item in inventory.pack %}
					<li>{{item.name}}</li>
					{% endfor %}
				</ul>
			</td>
			<td>
				<ul>
					{% for item in inventory.equipped %}
					<li>{{item.name}}</li>
					{% endfor %}
				</ul>
			</td>
			<td>
				<ul>
				{% for key, value in inventory.money.items() %}
					<li>{{value}} {{key}}</li>
				{%endfor%}
				</ul>
			</td>
		</tr>
		<tr>
			<td>
				{% if inventory.pack %}
				<form action="/INVENTORY" method="post">
					
					Manage Pack:
					<select name="equip">
						{% for item in inventory.pack %}
							<option value="{{item}}">{{item}}</option>
						{% endfor %}
					</select>
					<input type=submit name="todo" value="Equip Item">
					<input type=submit name="todo" value="Drop Item">
				</form>
				{%endif %}
			</td>
			<td>
				{% if inventory.equiped %}
				<form action="/INVENTORY" method="post">	
					Manage Equiped:
					<select name="equip">
						{% for item in inventory.equiped %}
							<option value="{{item}}">{{item}}</option>
						{% endfor %}
					</select>
					<input type=submit name="todo" value="Unequip Item">
				</form>
				{%endif %}
			</td>
			<td>
				<form action="/INVENTORY" method="post">
					Gold:<input type=text name="gold" size=5>
					Silver:<input type=text name="silver" size=5>
					Copper:<input type=text name="copper" size=5><br>
					<input type=submit name="todo" value="Add Money">
					<input type=submit name="todo" value="Spend Money">
			</td>
		</tr>
	</table>



