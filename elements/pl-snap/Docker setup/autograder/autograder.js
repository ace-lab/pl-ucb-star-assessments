const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer");

// Puppeteer PageFunctions.
function loadProject(projectXML) {
	const ide = world.children[0];
	ide.onNextStep = null;
	ide.world().animations = [];
	ide.rawOpenProjectString(projectXML);
}

function loadSprite(spriteXML) {
	world.children[0].rawOpenSpritesString(spriteXML);
}

function setTurboMode(turnOn) {
	const ide = world.children[0];
	if (turnOn) {
		ide.startFastTracking();
	} else {
		ide.stopFastTracking();
	}
}

function setEnableJSFunctions(boolean) {
	Process.prototype.enableJS = boolean;
	const ide = world.children[0];
	ide.flushBlocksCache('operators');
	ide.refreshPalette();
	ide.categories.refreshEmpty();
}

function grade(secretNumber) {
	const ide = world.children[0];
	const sprite = ide.sprites.asArray().at(-1);
	
	sprite.variables.setVar("secret number", 0);

	return new Promise((resolve) => {
		ide.broadcast("run autograder", () => {
			resolve(sprite.variables.getVar("results"));
		});
	});
}

// Utility function.
function readXML(filePath) {
	return fs.readFileSync(filePath).toString();
}

async function main() {
	console.time("Grading Time");
	console.log("Grading submission...");
	const url = "https://snap.berkeley.edu/snap/snap.html",
    	submissionPath = "/usr/src/cache/submission.xml",
    	resultsPath = "/grade/results/results.json",
    	autograderPath = "/grade/tests/autograder.xml",
		secretNumber = 0;

	let results;

	const browser = await puppeteer.launch({
		executablePath: "/usr/bin/google-chrome",
		args: ["--no-sandbox", "--disable-setuid-sandbox"],
	});
	const page = await browser.newPage();

	try {
		// Block unnecessary requests
		await page.setRequestInterception(true);
		page.on('request', (req) => {
			if (req.resourceType() === 'font' || req.resourceType() === 'image' || req.resourceType() === 'stylesheet') {
				req.abort();
			}
			else {
				req.continue();
			}
		});

		// page.on('console', msg => console.log('PAGE LOG:', msg.text()));

		console.time("Page Load Time")
		Promise.all([
			await page.goto(url, { waitUntil: "domcontentloaded" }),
			submission = readXML(submissionPath),
			autograder = readXML(autograderPath),
		]);
		console.timeLog("Page Load Time", "Page loaded");
		await Promise.all([
			page.evaluate(loadProject, submission),
			page.evaluate(loadSprite, autograder),
			page.evaluate(setTurboMode, true),
			page.evaluate(setEnableJSFunctions, true),
		]);
		console.timeLog("Page Load Time", "Project and Autograder loaded");
		results = await page.evaluate(grade, secretNumber);
		console.timeEnd("Page Load Time");
	} catch (e) {
		results = JSON.stringify({
			"score": 0,
			"output": (
				"Failed to grade submission. Make sure:\n" +
				"1) Your filename follows the specified format.\n" +
				"2) Your code doesn't cause any Snap! error.\n" +
				"3) Your code runs in a reasonable amount of time." +
				e
			)
		});
	} finally {
		// Define the directory path
		const dir = '/grade/results';

		// Create the directory if it doesn't exist
		if (!fs.existsSync(dir)) {
		fs.mkdirSync(dir, { recursive: true });
		}
		fs.writeFileSync(resultsPath, results);
		await browser.close();

		console.log("Grading completed.");
		console.timeEnd("Grading Time");
	}
}

if (typeof require !== "undefined" && require.main === module) {
	main();
}