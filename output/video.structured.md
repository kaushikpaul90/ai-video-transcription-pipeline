## Summary
- David Lithicum shares his experience with generative AI projects, such as recommendation engines and supply chain optimization.
- Clean, well-understood data is crucial for effective generative AI model training and performance.
- Ethical considerations, including bias, are discussed, highlighting the need for an ethics specialist in generative AI initiatives.
- Technical strategies for model optimization, evaluation, and managing limited or noisy data are explored.
- Generative AI is transforming marketing by enabling personalized content and enhancing demand generation.
- Attention mechanisms in generative models improve focus and performance through configurable parameters.
- Staying current in generative AI requires continuous learning from diverse sources, and resources like the Go Cloud Careers program support aspiring professionals.

## Introduction and Background

- Michael Gibbs introduces himself and David Lithicum.
- Michael has over 25 years as a network and enterprise architect; David has 35 years as an architect and CTO, and is an expert on generative AI.
- The session is a role-play interview focused on generative AI architect questions.

## Generative AI Project Experience

### Recommendation Engine for Retailer

- David describes a project for a large retailer: a recommendation engine using generative AI.
- The engine analyzes unregistered website visitors’ behavior to infer demographics and interests.
- Based on patterns from past customers, the system recommends products, increasing sales by 30% without requiring user registration.

### Supply Chain Integration During COVID

- David built a generative AI-driven supply chain integration system for a tire manufacturer.
- The system handled logistics planning, training, and optimization across tens of thousands of data points.
- Resulted in $30 million additional revenue in one quarter by optimizing the supply chain.

## Data Preparation for Generative AI

- Clean, well-understood data is critical for generative AI success.
- Data sources can include images, PDFs, customer, inventory, and sales data.
- Key steps: normalization, augmentation, dimensionality reduction, and metadata management.
- 90% of generative AI projects fail due to poor data hygiene and lack of investment in understanding data.
- Tools for data hygiene, metadata management, and integration are essential.

## Designing and Training Generative Adversarial Networks (GANs)

- GANs involve a generator and discriminator working adversarially to improve image (or text, etc.) generation.
- The process is iterative: the generator creates, the discriminator evaluates, and both improve over time.
- Architects typically select tools and approaches; engineers implement the details.
- GANs are used for various outputs, including images, text, and more.

## Ethical Considerations and Bias

- Ethical concerns include bias, deep fakes, and potential harm to individuals or society.
- David always includes an ethics specialist on generative AI projects to develop ethics plans and conduct bias audits.
- Generative AI systems should be built as if their decisions may need to be explained in court.
- Defensive ethics: audit, track, and log decisions to ensure accountability.

## Current State and Future of Generative AI

- The industry is currently focused on tactical tools, processors, and cloud providers.
- Long-term focus should shift to business applications and strategic value.
- Most businesses will use smaller, purpose-built models for specific domains.
- The real value lies in differentiating business processes, not just using the latest technology.

## Model Optimization and Performance

- Example: Optimizing the recommendation engine for speed and relevance.
- Techniques include residual connections, normalization, and avoiding overtraining or redundant knowledge.
- Purpose-built models should focus only on necessary domain knowledge.
- Modern tools automate much of the optimization; architects must plan and ensure proper processes.

## Types and Contexts of Generative Models

- David has worked with models generating images, text, videos, and logistics plans.
- Examples include personalized images/text for retail customers and supply chain process generation.
- Generative models are also used for fraud detection and security (e.g., identifying individuals from images).

## Assessing Quality of Generative Samples

- Quality assessment involves visual inspection, quantitative metrics, and domain-specific criteria.
- Testing tools can automate quality checks and provide feedback for model improvement.
- Similar to traditional software testing, but with more complexity due to generative outputs.

## Challenging Generative AI Projects

- David describes building a fraud detection system for a government agency as particularly challenging due to new technology and lack of resources.
- Required innovative approaches and adapting knowledge from other domains.

## Handling Bias and Legal Considerations

- Addressing bias involves ethical frameworks, guidelines, and regular audits.
- Legal considerations include consent, copyright, and ensuring no harm is done.
- An ethics specialist is responsible for auditing and ensuring responsible use.

## Latent Space in Generative Models

- Latent space is a low-dimensional work area where features and variations are processed during model training.
- Architects should understand its existence and ask vendors about its management, though implementation details are typically handled by tools.

## Conditional Generative Models

- Conditional models generate data based on specific conditions (e.g., conditional VAE for handwriting).
- Architects should understand the concept, but implementation is tool-dependent.

## Training with Limited or Noisy Data

- Strategies include transfer learning, data augmentation, and semi-supervised learning.
- Data should be cleaned or backfilled where possible; monitoring systems can help handle noisy data on the fly.

## Ensuring Stability and Convergence

- Techniques: normalization, progressive growth, adaptive learning rates, diversity-promoting loss functions, and preventing overfitting.
- Tools automate much of this, but architects must ensure proper configuration and reliability.

## Trade-offs Between Generative Models

- GANs (Generative Adversarial Networks) prioritize sample quality via adversarial training.
- VAEs (Variational Autoencoders) and other models have different strengths and trade-offs, which architects should understand at a conceptual level.

## Creative Applications and Scalability

- Generative AI enables creative outputs (e.g., custom art, diagrams, deep fakes) and business applications.
- Scalability and computational efficiency are critical; avoid simply throwing hardware at the problem.
- Optimize architecture for performance, cost, and resource utilization using distributed frameworks and appropriate hardware.

---

**End of Part 1**
## Real-World Applications of Generative Models

- Generative AI has had a significant, though often unpublicized, impact on marketing departments.
- These systems are used to generate demand, customize marketing stimuli, and improve sales by analyzing social media and other data sources.
- Marketing teams use generative AI to create custom images, text, and audio, allowing for more nuanced and less intrusive communication with customers.
- The integration of generative AI in marketing is strategic and typically not publicized, but it is quietly changing the industry.
- Other industries, such as supply chain management (e.g., Uber's AI for driver and car selection), are also leveraging generative AI for tactical improvements.

## Role of Attention Mechanisms in Generative Models

- Attention mechanisms help generative models focus on relevant information, improving output quality and efficiency.
- These models have tunable parameters (like learning rates and batch sizes) that can be configured for optimal performance, similar to tuning a database or an automobile.
- Best practices for configuring these parameters vary by toolset, and understanding them is key to maximizing system performance.

## Staying Updated with Generative AI Advancements

- Staying current involves reading widely, setting up Google alerts, watching videos, taking courses, and reading books.
- Engaging with content from vendors, attending conferences, and participating in online communities (e.g., LinkedIn, Reddit) provides diverse perspectives.
- The field is rapidly evolving, and much information is new or unfiltered, requiring discernment to identify valuable insights.
- Over time, more structured resources (books, training) will become available, but currently, it's important to sift through large volumes of information.

## Go Cloud Careers Generative AI Architect Program

- The program, authored by David Lithicum, covers technical and engineering aspects of generative AI architecture.
- Go Cloud Careers complements this with training in business acumen, leadership, sales, executive presence, emotional intelligence, presentation, negotiation, and stakeholder management.
- Free resources are available, including webinars on becoming a generative AI architect, cloud architect, or enterprise architect.
- Webinars cover required skills, hiring processes, and provide opportunities for direct interaction and guidance.
- Viewers are encouraged to like, subscribe, and join future sessions for ongoing support in their architect careers.

## How This Was Organized
- The transcript was processed in sequential parts and each part was structured into topical sections with headings and bullet points.
- Key points from every part were synthesized into a single deduplicated summary at the top.
- Filler and false starts were removed while preserving the original meaning.