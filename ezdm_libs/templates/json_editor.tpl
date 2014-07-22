<form action="{{header[action]}}" method="post"> 
<table border=1>
	<tr><td bgcolor=lightblue colspan=2>
		<center>
			<strong>
				{{header[name]}}
			</strong>
		</center>
		</td>
	</tr>
	{% for key in formdata|sort %}
	<tr>
		<td>
			{{formdata[key].name}}
		</td>
		<td>
			{% if formdata[key].inputtype == 'select' %}
				<select name="{{formdata[key].name}}">
					<option value="{{formdata[key].value}}">{{formdata[key].value}}</option>
					{% for value in formdata[key].options %}
						<option value="{{value}}">{{value}}</option>
					{%endfor%}
			{% else %}
				<input name="{{formdata[key].name}}"type="{{formdata[key].inputtype}}" value="{{formdata[key].value}}">
			{% endif %}
		</td>
	</tr>
	{% endfor %}
</table>
</form>

