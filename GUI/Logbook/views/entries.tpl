% rebase('base.tpl', title='List of entries')
<div class="container">
    <h1>List of Entries in the database</h1>
    <p>Here you can see all the entries that were added to the database of the Logbook. <br />There is still the need to add a method for adding and subtracting setups from it.</p>
    <table class="table">
        <thead>
            <tr>
                <th>Date</th>
                <th>User</th>
                <th>Setup</th>
                <th>Entry</th>
                <th>Detectors</th>
                <th>Variables</th>
            </tr>
        </thead>
        <tbody>
            % for entry in entries:
            <tr>
                <td>{{entry['Date']}}</td>
                <td>{{user[entry['User']]}}</td>
                <td>{{setup[entry['Setup']]}}</td>
                <td>{{entry['Entry']}}</td>
                <td>{{entry['Detectors']}}</td>
                <td>{{entry['Variables']}}</td>
                
            </tr>
            % end
        </tbody>
    </table>
</div>