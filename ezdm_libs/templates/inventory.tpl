<form id="clickform" method=post>
	<input type=hidden id="selected" name="selected" value="">
	<input type=hidden name="section" id="section" value="">
</form> 
<script>
    function clickHandler(x,y) {
        document.getElementById('selected').value = x;
        document.getElementById('section').value = y;
        document.getElementById('clickform').submit();
    }
</script>
<table border=1 width=100%>
	<tr>
		<td colspan=3 bgcolor=lightgray>
			<center><strong>Inventory for {{character}}</strong></center>
		</td>
	</tr>
	<tr>
		<td bgcolor=lightblue>
			Pack:
		</td>
		<td bgcolor=lightblue>
			Equiped:
		</td>
		<td bgcolor=lightblue>
			Detail View:
		</td>
	</tr>
	<tr>
		<td>
			<ul>
				{% for item in inventory.pack %}
				<li>
					<a href="#" onclick="clickHandler('{{loop.index -1}}', 'pack')">{{item.core.name}}</a>
					<img onclick="clickHandler('{{loop.index -1}}', 'pack')" src="/icon/{{item.core.icon}}"></li>
				{% endfor %}
			</ul>
			<ul>
				{% for k,v in inventory.money.items() %}
				<li>{{k}}: {{v}}</li>
				{% endfor %}
			</ul>			
			{% if editmode %}
			<br>
			<form method=post>
				<select name="acquire_item">
					{%for item in items|sort %}
					<option value="{{item}}">{{item}}</option>
					{%endfor%}
				</select>
				<input type=submit value="Acquire Item">
			</form>
			<form method=post>
				Gold:<input name="gold" type=text size=3 value="0"> 
				Silver:<input name="silver" type=text size=3 value="0"> 
				Copper:<input name="copper" type=text size=3 value="0"> 
				<input type=submit name="givemoney" value="Give Money">
			</form>
			{% endif %}
		</td>
		<td>
			<ul>
 				{%for slot in inventory.equiped %}
 					<li>{{slot}}
  						{% if 'core' in inventory.equiped[slot] %}
 						<ul>
 							<li>
								<a href="#" onclick="clickHandler('x', '{{slot}}')">{{inventory.equiped[slot].core.name}}</a>
 							</li>
 							<li>
 							<img onclick="clickHandler('x', '{{slot}}')" src="/icon/{{inventory.equiped[slot].core.icon}}">
 						</li>
 						</ul>
 						{%endif%}
 					</li>
 				{%endfor%}
			</ul>
		</td>
		<td width=40%>
			{% if detailview %}
				<ul>
				{%- for key, value in detailview.render().items() recursive %}                       
				<li>{{ key }}                                                           
				{%- if value is mapping %}                                                                                                
				  <ul>{{ loop(value.items())}}</ul>
				{% else %}
				     = {{value}}
				{%- endif %}                                                            
				</li>                                                                     
				{%- endfor %}   
				</ul><br>
				<form method=post>
					{% if not itemslot %}
					<input type=hidden name="pack_index" value="{{packindex}}">
					<input type=submit name="dropitem" value="Drop Item">
					<input type=submit name="equipitem" value="Equip Item">
					{% else %}
					<input type=hidden name="slot_name" value="{{itemslot}}">
					<input type=submit name="unequipitem" value="Unequip Item">
					{% endif%}
					<br/>
					{% if not editmode %}
					{% if detailview.get('/core/charges',0) != 0 %}
						<select name="useitem_target">
							{% for target in targetlist %}
								<option value="{{target.name()}}">{{target.displayname()}}</option>
							{% endfor %}
						</select>
						<input type=submit name="useitem" value="Use Item">
					{% endif %}
					{% endif %}
					{% if detailview.get('/core/in_use', False) %}
					<input type=submit name="stopusing" value="Stop using">
					{% endif %}
				</form>
			{% endif %}
	</td>
	</tr>
</table>