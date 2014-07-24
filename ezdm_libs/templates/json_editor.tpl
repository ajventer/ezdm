<form action="/action{{header.action}}" method="post"> 
<table border=1>
	<tr><td bgcolor=lightblue colspan=2>
		<center>
			<strong>
				{{header.name}}
			</strong>
		</center>
		</td>
	</tr>
	{% for key in formdata|sort(True) %}
	{% if  formdata[key].inputtype == "hidden" %}
		<input id="{{formdata[key].name}}" name="{{formdata[key].name}}" type="{{formdata[key].inputtype}}" value="{{formdata[key].value}}">
	{% else %}
	<tr>
		<td>
			{{formdata[key].name}}
		</td>
		<td>
			{% if formdata[key].inputtype == 'select' %}
				<select id="{{formdata[key].name}}" name="{{formdata[key].name}}">
					<option value="{{formdata[key].value}}">{{formdata[key].value}}</option>
					{% for value in formdata[key].options %}
						<option value="{{value}}">{{value}}</option>
					{%endfor%}
			{% elif formdata[key].inputtype == 'textarea' %}
				<textarea name="{{formdata[key].name}}" id="{{formdata[key].name}}">{{formdata[key].value}}</textarea>
			{% else %}
				<input id="{{formdata[key].name}}" name="{{formdata[key].name}}" type="{{formdata[key].inputtype}}" value="{{formdata[key].value}}">
			{% endif %}
		</td>
	</tr>
	{% endif %}
	{% endfor %}
	<tr>
		<td colspan=2><center>
			<input type=submit value="Save changes">
		</center>
		</td>
	</tr>
</table>
</form>



