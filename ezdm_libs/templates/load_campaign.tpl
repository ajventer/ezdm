</center>
<a href="/action/EZDM_CAMPAIGNS">New Campaign</a>
<ul>Load Existing Campaign
{% for campaign in campaigns %}
 <li><a href="/load_campaign/{{campaign}}">{{campaign}}</a></li>
{%endfor%}
</ul>