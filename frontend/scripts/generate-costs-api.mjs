import { generateApi } from 'swagger-typescript-api';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

await generateApi({
  fileName: 'CostsApi.ts',
  output: resolve('src/api/generated'),
  spec: JSON.parse(await readFile(resolve('openapi.json'), 'utf8')),
  httpClientType: 'axios',
  extractRequestParams: true,
});
