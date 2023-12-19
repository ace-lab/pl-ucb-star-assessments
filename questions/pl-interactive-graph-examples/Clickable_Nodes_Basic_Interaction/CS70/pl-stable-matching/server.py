import random, string, copy
import prairielearn as pl

# todo: make chart cross-offs persistent (?), feedback


def generate(data, n=4):
	# Generate a random n=4 stable matching instance
	data["params"]["jobs"] = list(map(str, list(range(1, n+1)))) # not sure why f-strings aren't working here
	data["params"]["candidates"] = list(string.ascii_uppercase)[:n]
	# highest day that should be shown to the student
	data["params"]["dayshow"] = 1
	data["params"]["done"] = False
	
	jobpref = {}
	candidatepref = {}
	for job in data["params"]["jobs"]:
		jobpref[job] = random.sample(data["params"]["candidates"], n)
	for candidate in data["params"]["candidates"]:
		candidatepref[candidate] = random.sample(data["params"]["jobs"], n)

	data["params"]["jobspref"] = jobpref
	data["params"]["candidatespref"] = candidatepref

	data["params"]["jobsrender"] = html_render(jobpref)
	data["params"]["candidatesrender"] = html_render(candidatepref)

	sma(data)
	return data


def html_render(dict):
	pref = []
	for entity in dict:
		pref.append({"name":f"{entity}", "preffirst":{"pref_name":f"{list(dict[entity])[0]}"}, "pref": [{"pref_name":f"{i}"}  for i in list(dict[entity])[1:]]})
	return pref


def sma(data):
	"""
	Runs SMA algorithm given supplied data parameters. Returns the final pairing as well as number 
	of days it took. 
	Stores day-by-day rejections in data["params"]["rejections"] mapping day -> [rejected jobs]
	"""
	data["params"]["rejections"] = {}
	jobspref = copy.deepcopy(data["params"]["jobspref"])
	# print(jobspref)
	rejections = -1
	daycount = 0
	#stores what happens in the day in the form
	# {"daynumber":1, 
	#  "proposals": [{"name":"day1proposals-1",  "candidates":{candidate:c, proposed:true}}...,"job":j}] 
	#  "rejections":[{"name":"day1rejections-c","rejectedjobs":[{"job":1, "rejected":"false"}...], "candidate":c}]}
	dayresults = [] 
	while rejections:
		daycount += 1
		visibility = "hidden" if daycount > data["params"]["dayshow"] else ""
		dayresults_entry = {"daynumber":daycount, "proposals":[], "rejections":[], "display":visibility}

		# create mapping of candidate (letter) to array of received offers
		cand_offers = {}
		for candidate in data["params"]["candidates"]:
			cand_offers[candidate] = []

		# each job proposes to their favorite candidate
		for job in data["params"]["jobs"]:
			fav = jobspref[job][0]
			cand_offers[fav].append(job)
			dayresults_entry["proposals"].append({"name":f"day{daycount}proposals-{job}","job":job, "candidates":
				[{"candidate":c, "proposed":"true"} if c == fav else {"candidate":c, "proposed":"false"} for c in data["params"]["candidates"]]})
			
			# hacky bugfix: manually set correct answers for all "hidden" days
			data["correct_answers"][f"day{daycount}proposals-{job}"] = fav


		# candidates reject all but their favorite job
		rejectedjobs = []
		for candidate in cand_offers:
			if len(cand_offers[candidate]) > 1:
				offers = set(cand_offers[candidate])
				fav_job = next((e for e in data["params"]["candidatespref"][candidate] if e in offers))
				# remove favorite offer from offers
				offers.remove(fav_job)

				# reject every job in the "leftover" offers category
				rejectedjobs.extend(offers)
				dayresults_entry["rejections"].append({"name":f"day{daycount}rejections-{candidate}","candidate":candidate,
					"rejectedjobs":[{"job":j, "rejected":"true"} if j in offers else {"job":j, "rejected":"false"} for j in data["params"]["jobs"]]})

				# hacky fix -- preprocess hidden checkbox items for future days
				if daycount > data["params"]['dayshow']:
					possibilities = []
					corrects = []

					for i, j in enumerate(data["params"]["jobs"]):
						possibilities.append({"key": pl.index2key(i), "html": j, "feedback": None})
						if j in offers:
							corrects.append({"key": pl.index2key(i), "html": j, "feedback": None})

					data["params"][f"day{daycount}rejections-{candidate}"] = possibilities
					data["correct_answers"][f"day{daycount}rejections-{candidate}"] = corrects

					

		rejections = len(rejectedjobs)
		data["params"]["rejections"][daycount] = rejectedjobs
		# print(rejectedjobs)

		# all rejected jobs cross off their favorite candidate
		for job in rejectedjobs:
			jobspref[job].pop(0)

		# add this day's entry if the student is allowed to see it.  Otherwise hacky bugfix
		if daycount <= data["params"]["dayshow"]:
			dayresults.append(dayresults_entry)

	# check if finished
	if data["params"]["dayshow"] > daycount:
		data["params"]["done"] = True
	#record final pairing as a string
	ret = ""
	for job in jobspref:
		ret += f'({job}, {jobspref[job][0]})'

	data["params"]["days_ans"] = [{"tag":"false", "ans":i} if i != daycount else {"tag":"true", "ans":i} for i in range(1,11)]
	data["params"]["dayresults"] = dayresults
	# print(dayresults)


def parse(data):
	pass
	
def grade(data):
	if data["score"] == 1 and not data["params"]["done"]:
		data["params"]["dayshow"]+=1
		sma(data)
		if not data["params"]["done"]:
			data["score"] = data["score"] *.95


"""
data = {}
data["params"] = {}
generate(data)
print(data)
print(sma())
"""
