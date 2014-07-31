</center>
<ul>
{% for campaign in campaigns %}
 <li><a href="/load_campaign/{{campaign}}">{{campaign}}</a></li>
{%endfor%}
</ul>