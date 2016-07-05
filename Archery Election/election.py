import csv
import numpy as np

if __name__ == "__main__":
    csvfile = 'Ballot.csv'
    threshold = 0.5
    verbose = False
    
    ballot_dict = {}
    job_list = []
    ballots_mtrx = np.array([])
    # read the csv file
    with open(csvfile, 'rb') as f:
        reader = csv.reader(f)
        first_row = 1
        for row in reader:
            if first_row:
                first_row = 0
                
                row = row[1:len(row)]
                for word in row:
                    (job,name) = word.split('[')
                    job = job.strip()
                    name = name.split(']')[0].strip()

                    if job not in ballot_dict:
                        ballot_dict[job] = []
                        job_list.append(job)
                    ballot_dict[job].append(name)

            else:
                row = row[1:len(row)]
                if ballots_mtrx.size==0:
                    ballots_mtrx = np.hstack((ballots_mtrx, np.array(row)))
                else:
                    ballots_mtrx = np.vstack((ballots_mtrx, np.array(row)))

    (num_voters,temp) = ballots_mtrx.shape

    num_jobs = len(job_list)
    winners = np.zeros(num_jobs)
    base_indx = 0
    ballot_winner = []
    for job_id in range(0,num_jobs):
        job_name = job_list[job_id]
        num_candidates = len(ballot_dict[job_name])
        ballots = ballots_mtrx[:, base_indx:base_indx+num_candidates]
        if verbose:
            print(job_name)
        base_indx = base_indx+num_candidates

        # start voting
        while True:
            if verbose:
                print ballots
            votes = np.argmin(ballots,1)
            ballots_tallied = np.zeros(num_candidates)
            for i in range(0,num_candidates):
                ballots_tallied[i] = sum(votes==i)

            # do we have a winner?
            if np.max(ballots_tallied)>num_voters*threshold:
                winners[job_id] = np.argmax(ballots_tallied)
                ballot_winner.append(ballot_dict[job_name][np.argmax(ballots_tallied)])
                break
            # redistribute the votes (i.e. remove a candidate)
            else:
                # find the most unpopular
                loser_val = np.min(ballots_tallied)
                loser_ids = np.where(ballots_tallied==loser_val)[0]
                num_candidates = num_candidates-len(loser_ids)
                # did the candidates tie?
                if num_candidates==0:
                    tie_str = "Tie between"
                    for finalist in ballot_dict[job_name]:
                        tie_str = tie_str + " " + finalist
                    ballot_winner.append(tie_str)
                    break
                
                for losers in loser_ids[::-1]:
                    ballots = np.delete(ballots,losers,1)
                    ballot_dict[job_name] = np.delete(ballot_dict[job_name],losers)

        
        if verbose:
            print num_candidates
            print(winners)

    for i in range(0,num_jobs):
        print(job_list[i])
        print(ballot_winner[i])
        print ""
