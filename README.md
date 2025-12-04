# **Projeto Radiologia DF: Monitoramento de Equipamentos Hospitalares**

## **Descrição do Projeto**

O Projeto Radiologia DF tem como objetivo desenvolver um painel interativo capaz de consolidar, interpretar e comunicar informações sobre a infraestrutura de diagnóstico por imagem da rede pública do Distrito Federal, em especial mamógrafos, aparelhos de raio-x e equipamentos relacionados à oncologia.

Segundo entidades como o Tribunal de Contas do Distrito Federal (TCDF) e o Sistema Único de Saúde (SUS), os sistemas de saúde do DF enfrentam problemas como baixa disponibilidade de equipamentos, altos tempos de espera. Além disso, os dados sobre saúde encontram-se fragmentados entre diversas plataformas como DATASUS, SISCAN, CNES e IBGE, dificultando a tomada de decisão estratégica por parte de gestores públicos. Outro fator crítico é que parte dessas plataformas opera em ambientes sem proteção HTTPS, o que compromete a criptografia da comunicação. Tal vulnerabilidade pode expor gestores e usuários a riscos como interceptação de dados, manipulação de informações e falhas de autenticidade, fatores incompatíveis com a criticidade dos dados de saúde pública.


O **Projeto Radiologia DF** busca resolver essa lacuna criando uma plataforma acessível, unificada, segura e interpretativa, capaz de apoiar:
- Gestores públicos, que necessitam de indicadores claros para planejamento e alocação de recursos;
- Pesquisadores e acadêmicos, que se beneficiam de dados integrados e análises estruturadas;  
- Pacientes e público geral, que ganham transparência sobre gargalos e desempenho da rede hospitalar;

A solução propõe:
- Centralização de dados sobre equipamentos e exames;
- Visualizações interpretativas sobre demanda, oferta, atrasos e gargalos;
- Análises preditivas sobre demanda futura (ex.: séries temporais ARIMA);
- Indicadores de eficiência e uso dos equipamentos;
- Avaliação de acessibilidade e usabilidade dos portais oficiais;

## **Metas:**
- **Coletar e Estruturar Dados:**  
  - Levantar informações dos equipamentos de radiologia e mamografia do DF.
  - Integrar dados dispersos das plataformas DATASUS, SISCAN, CNES, TABNET e IBGE.
  - Mapear tempos de espera, capacidade teórica x realizada e volume de exames.
  - Catalogar indicadores de manutenção, disponibilidade e inoperância.
  - Reunir dados de campanhas de conscientização (queda, trauma, oncologia).

- **Desenvolver Dashboard Interativo:**  
  - Visualizar atrasos de exames e gargalos regionais.
  - Exibir distribuição geográfica dos equipamentos.
  - Mostrar eficiência operacional (taxas de utilização, capacidade versus demanda).
  - Integrar análises diagnósticas e preditivas, incluindo:
    - projeção de demanda de exames até 2030 (ARIMA)
    - simulação de impacto de novos investimentos (+10 mamógrafos → redução de X% no tempo médio)
    - estimativa de depreciação e renovação da frota de equipamentos

- **Analisar Padrões e Tendências:**  
  - Identificar regiões críticas com escassez de equipamentos.
  - Relacionar falta de manutenção com atrasos e diminuição da capacidade produtiva.
  - Comparar DF com médias nacionais (benchmarking).

- **Justificar a Solução:**
  - Transformar dados dispersos em inteligência acessível, apoiando políticas públicas.
  - Criar recurso de transparência para sociedade e para pesquisas acadêmicas.
  - Fornecer dados e análises como base para recomendações que melhorem a gestão de equipamentos hospitalares.  

## **Membros da Equipe e Papéis**
| Membro              | Papel                      |
|---------------------|----------------------------|
| Pedro Klein         | Pesquisa                   |
| Henrique Lessa      | Pesquisa                   |
| Gabrielle Gutierres | Pesquisa / UX              |
| Thales Rassi        | Desenvolvimento / Pesquisa |
| Matheus Moraes      | Desenvolvimento / Pesquisa |
| Gabriel Marques     | Desenvolvimento / Pesquisa |

## **Estrutura do Repositório**
- **/design**: Mockups, imagens e elementos visuais do projeto.  
- **/docs**: Entregáveis, documentação, atas de reunião, especificações e afins.  
- **/database**: Arquivos dos dados coletados.  
- **/prototype**: Protótipos.  
- **/src**: Código-fonte principal do projeto.
