export function generatePigeonSearchTerm(): string {
  return `${generateAdjective()} pigeon`;
}

export function generateAdjective(): string {
  const adjectives = [
    "flying",
    "eating",
    "idle",
    "smart",
    "nice looking",
    "funny",
    "beautiful",
    "ugly",
    "cute",
    "adorable",
    "fierce",
    "angry",
    "happy",
    "sad",
    "sleepy",
    "hungry",
    "silly",
    "serious",
    "sneaky",
  ];
  return adjectives[Math.floor(Math.random() * adjectives.length)];
}
