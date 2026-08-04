import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const username = process.env.GITHUB_USERNAME || "jcone211";
const token = process.env.GITHUB_TOKEN;
const target = resolve("data/github_contributions.json");

if (!token) {
  console.warn("GITHUB_TOKEN is not set. Existing calendar data was kept unchanged.");
} else {
  const query = `
    query ContributionCalendar($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                color
              }
            }
          }
        }
      }
    }
  `;

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "User-Agent": "jcone211-portfolio-build"
    },
    body: JSON.stringify({ query, variables: { login: username } })
  });

  const payload = await response.json();
  if (!response.ok || payload.errors || !payload.data?.user) {
    throw new Error(`GitHub GraphQL request failed: ${JSON.stringify(payload.errors || payload)}`);
  }

  const calendar = payload.data.user.contributionsCollection.contributionCalendar;
  const data = {
    username,
    totalContributions: calendar.totalContributions,
    generatedAt: new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false }),
    weeks: calendar.weeks.map((week) => ({
      days: week.contributionDays.map((day) => ({
        date: day.date,
        count: day.contributionCount,
        color: day.color
      }))
    }))
  };

  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  console.log(`Updated ${target} for @${username}: ${data.totalContributions} contributions.`);
}