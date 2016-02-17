% rebase('base.tpl', title='List of users')
<div class="container">
	<h1>List of Users in the database</h1>
	<p>Here you can see all the users that were added to the database of the logbook. <br />There is still the need to add a method for adding and subtracting people from it.</p>
	<table class="table">
		<thead>
			<tr>
				<th>Date</th>
				<th>Name</th>
			</tr>
		</thead>
		<tbody>
			% for user in users:
			<tr><td>{{user['Date']}}</td><td>{{user['Name']}}</td></tr>
			%
		</tbody>
	</table>
</div>