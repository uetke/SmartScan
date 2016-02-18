% rebase('base.tpl', title='List of setups')
<div class="container">
	<h1>List of Setups in the database</h1>
	<p>Here you can see all the setups that were added to the database of the logbook. <br />There is still the need to add a method for adding and subtracting setups from it.</p>
	<table class="table">
		<thead>
			<tr>
				<th>Date</th>
				<th>Name</th>
				<th>Description</th>
				<th>File</th>
			</tr>
		</thead>
		<tbody>
			% for setup in setups:
			<tr>
				<td>{{setup['Date']}}</td>
				<td>{{setup['Name']}}</td>
				<td>{{setup['Description']}}</td>
				<td>{{setup['File']}}</td>
			</tr>
			% end
		</tbody>
	</table>
</div>